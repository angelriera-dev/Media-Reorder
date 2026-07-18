# Delta for File Discovery (CLI)

## MODIFIED Requirements

### Requirement: Metadata Extraction

The system MUST extract date metadata from media files using a waterfall strategy.
The system MUST also parse Google Photos JSON sidecar files (`.json` companion files exported by Google Takeout) as an additional metadata source.
The system MUST prioritize sidecar JSON `photoTakenTime.timestamp` over filesystem mtime but below EXIF data.

## ADDED Requirements

### Requirement: Batch Metadata Extraction

The system MUST call `exiftool` in batch mode (`exiftool -json <dir>`) rather than one subprocess per file.
The system MUST cache extracted metadata in a local SQLite database keyed by `(file_path, mtime)` to avoid re-processing unchanged files on subsequent runs.
The system expects `exiftool` to be available in the system PATH.
