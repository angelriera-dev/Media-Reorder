# Tags Specification

## Purpose

Allow users to attach reusable personal labels to files in the history tree.
Tags are independent of technical metadata (EXIF, Google Drive) and coexist
alongside them in the detail panel. Tags are persisted in two places: the
SQLite database for fast search and filtering, and inside the file's own
metadata fields (XMP:Subject / IPTC:Keywords) for portability — so the tag
travels with the file regardless of where it is moved.

## Requirements

### Requirement: Tag Library

The system MUST maintain a user-defined tag library stored in the SQLite database.
Each tag MUST have a unique name (case-insensitive, max 64 characters).
The system MUST allow creating, renaming, and deleting tags from the library.
Deleting a tag from the library MUST remove it from all associated files.

#### Scenario: User creates a new tag

- GIVEN the tag panel is open
- WHEN the user types "viajes" and confirms
- THEN "viajes" is added to the tag library and available for assignment

#### Scenario: Duplicate tag name

- GIVEN "viajes" already exists in the library
- WHEN the user tries to create "Viajes"
- THEN the system rejects it with "Tag already exists"

### Requirement: Tag Assignment

The system MUST allow assigning one or more tags from the library to any file
in the history tree.
Tags MUST be displayed in the file detail panel alongside EXIF and Google Drive
metadata, visually distinct from system metadata fields.
The system MUST NOT overwrite or mix user tags with EXIF or Google Drive fields.

#### Scenario: User assigns a tag from the detail panel

- GIVEN a file detail panel is open
- WHEN the user clicks "Add tag" and selects "cumpleanos de sofi" from the library
- THEN the tag appears in the tags section of the detail panel
- AND the assignment is saved to the database

#### Scenario: User assigns a tag not yet in the library

- GIVEN the user types "universidad" which does not exist yet
- WHEN they confirm
- THEN "universidad" is created in the library AND assigned to the file in one step

### Requirement: Tag Writeback to File Metadata

The system SHOULD write assigned tags to the file's embedded metadata using
`exiftool` (XMP:Subject for images; XMP tags for MP4/MOV).
Writeback MUST be non-destructive — existing EXIF fields MUST NOT be modified.
If writeback fails for a file (e.g., read-only, unsupported format), the tag
MUST still be saved in the SQLite database and the failure logged silently.

#### Scenario: Tag written to image metadata

- GIVEN the user assigns tag "viajes" to a JPEG file
- WHEN the assignment is saved
- THEN `exiftool -XMP:Subject="viajes" file.jpg` is executed on the destination file
- AND the tag is readable by external apps (Lightroom, Apple Photos)

#### Scenario: Writeback fails — file is read-only

- GIVEN the destination file has read-only permissions
- WHEN writeback is attempted
- THEN the tag is saved in SQLite
- AND a silent log entry records the failure
- AND no error is shown to the user unless they inspect the file detail

#### Scenario: Tag removed — writeback clears field

- GIVEN a file has tag "jorge" written to XMP:Subject
- WHEN the user removes the tag
- THEN `exiftool` removes "jorge" from XMP:Subject on the destination file
- AND the tag is removed from the SQLite record

### Requirement: Tag Filtering

The system MUST allow filtering the file tree by one or more tags.

#### Scenario: User filters by tag

- GIVEN files have different tags assigned
- WHEN the user selects "viajes" from the filter panel
- THEN only files tagged "viajes" (and their parent directories) are shown

#### Scenario: User filters by multiple tags

- GIVEN the user selects both "viajes" and "jorge"
- WHEN the filter is applied
- THEN files tagged with either tag are shown (OR logic)
