# Delta for File Discovery

## MODIFIED Requirements

### Requirement: Metadata Extraction

The system MUST extract date metadata from media files using a waterfall strategy.
The system MUST also parse Google Photos JSON sidecar files (`.json` companion
files exported by Google Takeout) as an additional metadata source.
The system MUST prioritize sidecar JSON `photoTakenTime.timestamp` over filesystem
mtime but below EXIF data.
(Previously: no sidecar JSON support; only EXIF, binary, Pillow, filename, mtime)

#### Scenario: EXIF data present — sidecar ignored

- GIVEN a media file with valid EXIF DateTimeOriginal
- WHEN the organizer processes the file
- THEN the EXIF date is used and the sidecar JSON is not read

#### Scenario: No EXIF, sidecar present

- GIVEN a media file without EXIF and a companion `filename.json` in the same directory
- WHEN the organizer processes the file
- THEN `photoTakenTime.timestamp` from the JSON is parsed as the photo date

#### Scenario: No EXIF, no sidecar, filename pattern matches

- GIVEN a media file without EXIF and no companion JSON
- WHEN the organizer processes the file
- THEN the existing filename pattern / mtime fallback is used

#### Scenario: Sidecar JSON is malformed

- GIVEN a companion `.json` file that is not valid JSON or missing `photoTakenTime`
- WHEN the organizer attempts to parse it
- THEN the sidecar is silently skipped and the next fallback strategy is tried

## ADDED Requirements

### Requirement: Bundled exiftool

The system MUST bundle the `exiftool` binary inside the application package
for all supported platforms (Windows: `exiftool.exe`, Linux/macOS: `exiftool`).
The application MUST use the bundled binary exclusively — it MUST NOT depend on
any system-installed `exiftool`.
The bundled binary path MUST be resolved at runtime relative to the application
executable location.

#### Scenario: Fresh install, no system exiftool

- GIVEN a machine with no `exiftool` installed
- WHEN the application launches
- THEN metadata extraction works using the bundled binary
- AND no error or warning about missing exiftool is shown

#### Scenario: System exiftool exists alongside bundled

- GIVEN a machine where the user also has exiftool in PATH
- WHEN the application runs
- THEN the bundled binary is used, not the system one

### Requirement: Batch Metadata Extraction

The system MUST call `exiftool` in batch mode (`exiftool -json <dir>`) rather
than one subprocess per file.
The system MUST cache extracted metadata in a local SQLite database keyed by
`(file_path, mtime)` to avoid re-processing unchanged files on subsequent runs.

#### Scenario: First run on directory

- GIVEN a source directory with 1,000 image files and no cache
- WHEN the organizer starts
- THEN a single `exiftool` subprocess is spawned for the directory
- AND results are persisted to the SQLite cache before copying begins

#### Scenario: Re-run on same directory, files unchanged

- GIVEN a cache populated from a previous run and no file modifications
- WHEN the organizer starts
- THEN `exiftool` is NOT called
- AND metadata is read entirely from the SQLite cache

#### Scenario: Re-run with some files modified

- GIVEN a cache and 3 files whose mtime changed since last run
- WHEN the organizer starts
- THEN `exiftool` is called only for the 3 changed files
- AND the cache is updated for those files only
