# File Tree Specification

## Purpose

Provide a persistent, cached view of all copy operations — what was copied,
from where, and when — with the ability to inspect origins, preview media,
and manage source files.

## Requirements

### Requirement: Copy History Persistence

The system MUST record every copy operation in a SQLite database with:
`source_path`, `destination_path`, `source_parent_dir`, `copy_date`,
`file_size`, `date_taken`.
The system MUST persist this history across application restarts.

#### Scenario: File is copied during an organize run

- GIVEN the user runs an organize operation
- WHEN a file is successfully copied to the destination
- THEN a record is written to the history database including `source_parent_dir`

#### Scenario: Application restarted

- GIVEN the history database exists from a previous session
- WHEN the application launches
- THEN the file tree is populated from the database without re-scanning

### Requirement: File Detail Panel

The system MUST display a detail panel when the user clicks any file in the tree.
The detail panel MUST show:
- Inline media preview (image rendered, video playable)
- Metadata from the database (date copied, date taken, file size)
- EXIF metadata (camera model, dimensions, GPS if present)
- Google Drive sidecar data if a `.json` companion was parsed for this file
- Source origin path

#### Scenario: User clicks a file in the tree

- GIVEN the file tree shows organized files
- WHEN the user clicks on an image file
- THEN the detail panel opens showing the media preview and all available metadata
- AND Google Drive fields (description, geo) appear only if sidecar data exists

#### Scenario: User clicks a video file

- GIVEN the file tree shows a copied video
- WHEN the user clicks on it
- THEN the detail panel shows the video player in paused state with controls
- AND metadata fields are shown alongside the player

### Requirement: Source Origin Panel

The system MUST display the source origin path for each file in the detail panel.
The system MUST indicate if the source file no longer exists at the original path.
The system MUST allow expanding the origin to see sibling files — all files
that share the same `source_parent_dir` — without copying or duplicating them.
Sibling files are referenced by path only (foreign key), not stored as copies.

#### Scenario: User expands the origin panel

- GIVEN a file's detail panel is open showing source path `/media/card/DCIM/`
- WHEN the user expands the origin section
- THEN all files recorded with `source_parent_dir = /media/card/DCIM/` are listed
- AND the user can click any sibling to navigate to its own detail panel
- AND siblings that were also copied show a "copied" badge

#### Scenario: Source file no longer exists

- GIVEN the source device or path is no longer mounted
- WHEN the detail panel renders the origin
- THEN a "Source unavailable" indicator is shown
- AND the sibling list is still shown from the database record (path only)

#### Scenario: Source parent had 200 sibling files

- GIVEN a source directory with many files
- WHEN the origin panel is expanded
- THEN siblings are listed with virtual scroll — no UI freeze

### Requirement: Delete Source Option

The system MUST allow deleting the source file from the origin panel after
verifying copy integrity (size match AND SHA-256 hash match).
The system MUST require explicit confirmation before deleting.
The system MUST record the deletion in the history database.
The system MUST NOT delete the destination file — only the source.

#### Scenario: User deletes source, integrity passes

- GIVEN a file has been copied and source still exists
- WHEN the user selects "Delete source" and confirms
- THEN SHA-256 of source and destination are compared
- AND if they match, the source file is deleted
- AND the deletion timestamp is recorded in the database

#### Scenario: Integrity check fails before delete

- GIVEN the copied file hash does not match the source
- WHEN the user requests "Delete source"
- THEN deletion is blocked
- AND an error "Integrity check failed — source not deleted" is shown

### Requirement: Default Output Directory

The system MUST default the output directory to:
- Windows: `C:\Users\{username}\reorder`
- Linux / macOS: `~/reorder`
The system MUST create this directory if it does not exist on first run.
The system MUST allow the user to override this path in settings.

#### Scenario: First launch on Linux

- GIVEN the application is launched for the first time on Linux
- WHEN no output directory is configured
- THEN `~/reorder` is created if absent and set as the default output path

#### Scenario: User overrides output directory

- GIVEN the user opens settings and selects a different folder
- WHEN they confirm the selection
- THEN the new path is persisted and used for all subsequent organize runs
