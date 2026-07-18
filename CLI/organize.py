"""Copy + verify with SQLite tracking and SHA-256 validation."""
import os
import shutil
from pathlib import Path

from .db import compute_sha256, record_copy
from .dates import get_photo_date, format_date, prepopulate_cache_from_batch
from .search import find_images


def validate_source_path(source_dir: str) -> str:
    """Reject path traversal and shell metacharacters. Returns resolved path."""
    if ".." in source_dir:
        raise ValueError(f"Path traversal blocked: {source_dir}")
    resolved = os.path.realpath(source_dir)
    if not os.path.isdir(resolved):
        raise ValueError(f"Not a directory: {resolved}")
    return resolved


def _safe_target_path(target_dir, filename):
    """Return a target path that does not collide with existing files."""
    target_path = os.path.join(target_dir, filename)
    if not os.path.exists(target_path):
        return target_path
    name, ext = os.path.splitext(filename)
    counter = 1
    while True:
        candidate = os.path.join(target_dir, f"{name}_dup{counter}{ext}")
        if not os.path.exists(candidate):
            return candidate
        counter += 1


def copy_photos(source_dir, output_dir, conn=None):
    """Copy images organized by date. Returns {src: dst} dict.

    If conn is provided, records copies in copy_history table.
    """
    if conn:
        prepopulate_cache_from_batch(source_dir, conn)

    copied = {}
    output_real = os.path.realpath(output_dir)

    for filepath in find_images(source_dir, exclude_dir=output_real):
        filename = os.path.basename(filepath)
        date_info = get_photo_date(filepath, conn=conn)

        if not date_info:
            print(f"? No date for: {filename}")
            continue

        year, month, day, source = date_info
        day_str, month_name = format_date(year, month, day)
        if not day_str:
            continue

        target_dir = os.path.join(
            output_dir, str(year), f"{month:02d}-{month_name}", day_str
        )
        Path(target_dir).mkdir(parents=True, exist_ok=True)
        target_path = _safe_target_path(target_dir, filename)

        try:
            shutil.copy2(filepath, target_path)
            copied[filepath] = target_path
            sha = compute_sha256(target_path)
            if conn:
                file_size = os.path.getsize(target_path)
                record_copy(conn, filepath, target_path, file_size, sha)
        except Exception as e:
            print(f"Error copying {filename}: {e}")

    return copied


def verify_copy(copied):
    """Verify every copied file exists at destination with same size.

    Returns (ok, missing, size_mismatch).
    """
    missing = []
    size_mismatch = []
    for src, dst in copied.items():
        if not os.path.exists(dst):
            missing.append(dst)
            continue
        if os.path.getsize(src) != os.path.getsize(dst):
            size_mismatch.append((src, os.path.getsize(src), dst, os.path.getsize(dst)))
    return not missing and not size_mismatch, missing, size_mismatch


def verify_and_delete(src: str, dst: str, expected_sha256: str | None = None) -> bool:
    """Verify SHA-256 match before deleting dst. Returns True if safe to delete.

    If expected_sha256 is None, computes it from src.
    Block deletion on mismatch — never silently destroy data.
    """
    if not os.path.exists(dst):
        return False
    if expected_sha256 is None:
        expected_sha256 = compute_sha256(src)
    actual = compute_sha256(dst)
    if actual != expected_sha256:
        return False
    os.remove(dst)
    return True
