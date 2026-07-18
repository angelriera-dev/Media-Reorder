# Google Drive Import Specification (CLI)

## Purpose

Parse Google Takeout / Google Photos export sidecar `.json` files to extract accurate photo dates and metadata not available in EXIF.

## Requirements

### Requirement: Sidecar Discovery

The system MUST detect companion `.json` files following Google Takeout naming conventions alongside media files:
- `photo.jpg` → `photo.jpg.json`
- `photo(1).jpg` → `photo(1).jpg.json`

### Requirement: Sidecar Metadata Extraction

The system MUST extract `photoTakenTime.timestamp` (Unix epoch) from the Google sidecar JSON as a date source.
The system SHOULD also extract `description`, `geoData.latitude`, `geoData.longitude`, and `title` when present and store them in the metadata cache.