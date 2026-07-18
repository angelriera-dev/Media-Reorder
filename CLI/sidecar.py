"""Google Takeout sidecar JSON parser.

Finds {file}.json companions and extracts photoTakenTime.timestamp.
"""
import json
from datetime import datetime
from pathlib import Path


def sidecar_path(media_path: str | Path) -> Path | None:
    """Return the Google Takeout sidecar path for a media file, or None."""
    p = Path(media_path)
    # 1. Exact match with .json suffix
    candidate = p.parent / f"{p.name}.json"
    if candidate.is_file():
        return candidate
    # 2. Check for supplemental metadata json files
    if p.parent.exists():
        for path in p.parent.iterdir():
            if path.is_file() and path.name.startswith(p.name) and path.name.endswith(".json"):
                return path
    return None


def parse_sidecar(json_path: str | Path) -> dict | None:
    """Parse a Google Takeout sidecar JSON. Returns extracted fields or None."""
    try:
        data = json.loads(Path(json_path).read_text())
    except (json.JSONDecodeError, OSError):
        return None

    result = {}

    # photoTakenTime.timestamp (Unix epoch)
    ts = (data.get("photoTakenTime") or {}).get("timestamp")
    if ts:
        try:
            dt = datetime.fromtimestamp(int(ts))
            result["photo_taken"] = dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, OSError):
            pass

    # Optional fields
    if data.get("description"):
        result["description"] = data["description"]
    if data.get("title"):
        result["title"] = data["title"]
    geo = data.get("geoData") or {}
    if geo.get("latitude") and geo.get("longitude"):
        result["latitude"] = geo["latitude"]
        result["longitude"] = geo["longitude"]

    return result or None


def get_sidecar_date(media_path: str | Path) -> str | None:
    """Convenience: return photoTakenTime as a string, or None."""
    sp = sidecar_path(media_path)
    if not sp:
        return None
    parsed = parse_sidecar(sp)
    return (parsed or {}).get("photo_taken")
