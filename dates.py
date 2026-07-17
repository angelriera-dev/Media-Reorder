import os
import re
from datetime import datetime

import exifread

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


def _from_metadata(filepath):
    try:
        with open(filepath, "rb") as f:
            tags = exifread.process_file(f, stop_tag="EXIF DateTimeOriginal")
        date_str = str(tags.get("EXIF DateTimeOriginal", ""))
        match = re.search(r"(\d{4}):(\d{2}):(\d{2})", date_str)
        if match:
            return tuple(map(int, match.groups()))
    except:
        pass
    return None


def _from_filename(filename):
    patterns = [
        r"(\d{4})(\d{2})(\d{2})",
        r"(\d{4})-(\d{2})-(\d{2})",
        r"(\d{4})_(\d{2})_(\d{2})",
    ]
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            try:
                return tuple(int(g) for g in match.groups())
            except:
                pass
    return None


def _from_mtime(filepath):
    try:
        dt = datetime.fromtimestamp(os.path.getmtime(filepath))
        return (dt.year, dt.month, dt.day)
    except:
        return None


def get_date(filepath):
    """Returns (year, month, day) in priority: EXIF > filename > mtime."""
    return (
        _from_metadata(filepath)
        or _from_filename(os.path.basename(filepath))
        or _from_mtime(filepath)
    )


def format_date(year, month, day):
    """Returns (day_str, month_name) like ('11-Thu', 'Sep') or (None, None)."""
    try:
        dt = datetime(year, month, day)
        return f"{dt.day:02d}-{DAYS[dt.weekday()]}", MONTHS[month - 1]
    except:
        return None, None
