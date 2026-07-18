import os
import shutil
import subprocess
from pathlib import Path

from dates import get_photo_date, format_date
from search import find_images


def _safe_target_path(target_dir, filename):
    """Returns a target path that does not collide with existing files."""
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


def copy_photos(source_dir, output_dir):
    """Copy images from source_dir into output_dir organized by date.
    
    Returns a dict mapping source_filepath → dest_filepath for every
    successfully copied file (used by verify_copy).
    """
    copied = {}  # {src: dst}
    output_real = os.path.realpath(output_dir)

    for filepath in find_images(source_dir, exclude_dir=output_real):
        filename = os.path.basename(filepath)
        date_info = get_photo_date(filepath)

        if not date_info:
            print(f"⚠ No se pudo determinar fecha para: {filename}")
            continue

        year, month, day, source = date_info
        print(f"  ✓ Encontrada vía [{source}]: {year}-{month:02d}-{day:02d}")

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
            print(f"✓ Copiado: {filename} → {target_dir}")
        except Exception as e:
            print(f"✗ Error copiando {filename}: {e}")

    return copied


def verify_copy(copied):
    """Verify every copied file exists at destination with the same size.

    Args:
        copied: dict {src_path: dst_path} returned by copy_photos.

    Returns:
        (ok: bool, missing: list, size_mismatch: list)
    """
    missing = []
    size_mismatch = []

    for src, dst in copied.items():
        if not os.path.exists(dst):
            missing.append(dst)
            continue
        src_size = os.path.getsize(src)
        dst_size = os.path.getsize(dst)
        if src_size != dst_size:
            size_mismatch.append((src, src_size, dst, dst_size))

    ok = not missing and not size_mismatch
    return ok, missing, size_mismatch


def compress_backup(source_dir, output_dir):
    """Compress source_dir into a tar.gz."""
    print(f"\nComprimiendo {source_dir}...")
    try:
        subprocess.run(
            [
                "tar", "-czf", f"{output_dir}/backup.tar.gz",
                "-C", os.path.dirname(source_dir), os.path.basename(source_dir),
            ],
            check=True,
        )
        print(f"✓ Comprimido en: {output_dir}/backup.tar.gz")
    except Exception as e:
        print(f"✗ Error comprimiendo: {e}")

