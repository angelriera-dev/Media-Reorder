# Google Drive Import Specification

## Purpose

Parse Google Takeout / Google Photos export sidecar `.json` files to extract
accurate photo dates and metadata not available in EXIF.

## Requirements

### Requirement: Sidecar Discovery

The system MUST detect companion `.json` files following Google Takeout naming
conventions alongside media files:
- `photo.jpg` → `photo.jpg.json`
- `photo(1).jpg` → `photo(1).jpg.json`
The system MUST NOT treat arbitrary `.json` files in the source directory as
Google sidecars — only files matching the `{medianame}.json` pattern.

#### Scenario: Standard sidecar found

- GIVEN `IMG_0001.jpg` and `IMG_0001.jpg.json` exist in the same directory
- WHEN the organizer scans the source
- THEN `IMG_0001.jpg.json` is associated with `IMG_0001.jpg`

#### Scenario: Numbered duplicate sidecar

- GIVEN `IMG_0001(1).jpg` and `IMG_0001(1).jpg.json`
- WHEN the organizer scans the source
- THEN the numbered sidecar is correctly associated with the numbered file

### Requirement: Sidecar Metadata Extraction

The system MUST extract `photoTakenTime.timestamp` (Unix epoch) from the
Google sidecar JSON as a date source.
The system SHOULD also extract `description`, `geoData.latitude`,
`geoData.longitude`, and `title` when present and store them in the
metadata cache.

#### Scenario: Valid sidecar with photoTakenTime

- GIVEN a sidecar JSON with `{ "photoTakenTime": { "timestamp": "1609459200" } }`
- WHEN the organizer parses it
- THEN the photo date is set to 2021-01-01

#### Scenario: Sidecar missing photoTakenTime

- GIVEN a sidecar JSON that lacks the `photoTakenTime` key
- WHEN the organizer parses it
- THEN this metadata source is skipped and the next fallback is tried

#### Scenario: Sidecar JSON has unexpected schema version

- GIVEN a sidecar with an unrecognized top-level structure
- WHEN the organizer attempts to parse it
- THEN a warning is logged: "Unrecognized Google sidecar format: {filename}"
- AND the file is processed using remaining fallback strategies
