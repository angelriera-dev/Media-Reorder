"""Metadata extraction with batch exiftool, SQLite cache, and sidecar fallback.

Waterfall: sidecar JSON → exiftool → binary EXIF → filename → filesystem.
"""
import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

from .sidecar import get_sidecar_date

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


def _parse_date_string(text):
    """Extract (year, month, day) from multiple date formats."""
    patterns = [
        r"(\d{4}):(\d{2}):(\d{2})",
        r"(\d{4})-(\d{2})-(\d{2})",
        r"(\d{4})/(\d{2})/(\d{2})",
        r"(\d{2})/(\d{2})/(\d{4})",
    ]
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, text)
        if match:
            groups = list(map(int, match.groups()))
            if i == 3:
                groups = [groups[2], groups[1], groups[0]]
            return tuple(groups[:3])
    return None


def _is_reasonable_date(date_tuple):
    """Reject absurd dates (future, very old, epoch)."""
    y, m, d = date_tuple
    now = datetime.now()
    if y < 1990 or y > now.year:
        return False
    if m < 1 or m > 12 or d < 1 or d > 31:
        return False
    if y == 1970 and m == 1 and d == 1:
        return False
    return True


def _from_exiftool(filepath):
    """Extract date via exiftool priority tags."""
    PRIORITY_TAGS = [
        "DateTimeOriginal", "CreateDate", "ModifyDate",
        "XMP:DateCreated", "XMP:CreateDate", "XMP:DateTimeOriginal",
        "IPTC:DateCreated", "IPTC:DigitalCreationDate",
        "MediaCreateDate", "TrackCreateDate",
    ]
    cmd = ["exiftool", "-S", "-s"] + [f"-{t}" for t in PRIORITY_TAGS] + [filepath]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        for line in result.stdout.splitlines():
            date = _parse_date_string(line)
            if date and _is_reasonable_date(date):
                return date
    except Exception:
        pass
    return None


def batch_exiftool(directory: str | Path) -> list[dict]:
    """Run exiftool -json on a directory. Returns list of metadata dicts."""
    try:
        result = subprocess.run(
            ["exiftool", "-json", "-r", str(directory)],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return []


def prepopulate_cache_from_batch(directory: str | Path, conn) -> None:
    """Prepopulate SQLite metadata cache using a single batch exiftool run."""
    if not conn:
        return
    results = batch_exiftool(directory)
    if not results:
        return
    PRIORITY_TAGS = [
        "DateTimeOriginal", "CreateDate", "ModifyDate",
        "XMP:DateCreated", "XMP:CreateDate", "XMP:DateTimeOriginal",
        "IPTC:DateCreated", "IPTC:DigitalCreationDate",
        "MediaCreateDate", "TrackCreateDate",
    ]
    for item in results:
        src_file = item.get("SourceFile")
        if not src_file:
            continue
        if os.path.isabs(src_file):
            abs_path = os.path.realpath(src_file)
        else:
            abs_path = os.path.realpath(os.path.join(str(directory), src_file))
        if not os.path.exists(abs_path):
            abs_path = os.path.realpath(src_file)
            if not os.path.exists(abs_path):
                continue
        
        exif_date = None
        for tag in PRIORITY_TAGS:
            val = item.get(tag)
            if val:
                date = _parse_date_string(str(val))
                if date and _is_reasonable_date(date):
                    exif_date = f"{date[0]}:{date[1]:02d}:{date[2]:02d}"
                    break
        try:
            mtime = os.path.getmtime(abs_path)
            from .db import cache_metadata
            cache_metadata(
                conn, abs_path, mtime,
                exif_date=exif_date,
                raw_json=json.dumps(item),
            )
        except Exception:
            pass


def _from_jpeg_binary(filepath):
    """Read EXIF date from raw JPEG bytes."""
    try:
        with open(filepath, "rb") as f:
            data = f.read(65536)
        text = data.decode("latin-1", errors="ignore")
        match = re.search(r"(\d{4}):([01]\d):([0-3]\d) \d{2}:\d{2}:\d{2}", text)
        if match:
            date = tuple(map(int, match.groups()))
            if _is_reasonable_date(date):
                return date
    except Exception:
        pass
    return None


def _from_filename(filepath):
    """Extract date from filename patterns."""
    name = Path(filepath).stem
    patterns = [
        r"(?:IMG|VID|PXL|MVIMG|SAVE|Screenshot)[_-](\d{4})(\d{2})(\d{2})",
        r"(\d{4})-(\d{2})-(\d{2})",
        r"^(\d{4})(\d{2})(\d{2})[_\-]",
        r"photo[_-](\d{4})-(\d{2})-(\d{2})",
    ]
    for pattern in patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            date = tuple(map(int, match.groups()))
            if _is_reasonable_date(date):
                return date
    # Unix timestamp in name
    ts_match = re.search(r"(\d{13})", name)
    if ts_match:
        try:
            dt = datetime.fromtimestamp(int(ts_match.group(1)) / 1000)
            date = (dt.year, dt.month, dt.day)
            if _is_reasonable_date(date):
                return date
        except (ValueError, OSError):
            pass
    return None


def _from_filesystem(filepath):
    """Fallback: use file mtime."""
    try:
        stat = os.stat(filepath)
        ts = min(stat.st_mtime, stat.st_ctime)
        dt = datetime.fromtimestamp(ts)
        return (dt.year, dt.month, dt.day)
    except Exception:
        return None


def get_photo_date(filepath, conn=None):
    """Get the earliest reasonable date found across all metadata sources.
    
    Sources: sidecar, EXIF, binary, filename, filesystem.
    """
    file_path_str = os.path.realpath(filepath)
    mtime = os.path.getmtime(filepath)
    
    found_dates = []

    # 1. Try Cache/Sidecar
    if conn:
        from .db import get_cached_metadata
        cached = get_cached_metadata(conn, file_path_str, mtime)
        if cached:
            exif_date, sidecar_date, _ = cached
            for d in [exif_date, sidecar_date]:
                if d:
                    date = _parse_date_string(d)
                    if date and _is_reasonable_date(date):
                        found_dates.append(date)

    # 2. Extract from all sources
    # Sidecar (if not from cache)
    sidecar_date = get_sidecar_date(filepath)
    if sidecar_date:
        date = _parse_date_string(sidecar_date)
        if date and _is_reasonable_date(date):
            found_dates.append(date)
    
    # EXIF
    date = _from_exiftool(filepath)
    if date and _is_reasonable_date(date):
        found_dates.append(date)
        
    # Binary
    date = _from_jpeg_binary(filepath)
    if date and _is_reasonable_date(date):
        found_dates.append(date)
        
    # Filename
    date = _from_filename(filepath)
    if date and _is_reasonable_date(date):
        found_dates.append(date)
        
    # Filesystem
    date = _from_filesystem(filepath)
    if date and _is_reasonable_date(date):
        found_dates.append(date)

    if not found_dates:
        # Cache empty result to avoid re-processing
        if conn:
            from .db import cache_metadata
            cache_metadata(conn, file_path_str, mtime)
        return None
        
    # Find earliest date
    earliest = min(found_dates, key=lambda d: datetime(d[0], d[1], d[2]))
    
    # Update cache if needed
    if conn:
        from .db import cache_metadata
        # Re-save with the 'best' date found (using EXIF as fallback if needed)
        cache_metadata(conn, file_path_str, mtime, exif_date=f"{earliest[0]}:{earliest[1]:02d}:{earliest[2]:02d}")
        
    return (*earliest, "min_of_all")


def format_date(year, month, day):
    """Returns (day_str, month_name) or (None, None)."""
    try:
        dt = datetime(year, month, day)
        return f"{dt.day:02d}-{DAYS[dt.weekday()]}", MONTHS[month - 1]
    except Exception:
        return None, None
