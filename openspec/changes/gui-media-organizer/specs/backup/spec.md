# Backup Specification

## Purpose

Provide reversible point-in-time snapshots of the organized output directory
and database, stored outside `~/reorder`, using bundled `restic`. The user
can restore to any previous snapshot if files are lost or corrupted.

## Requirements

### Requirement: Bundled restic

The system MUST bundle the `restic` binary inside the GUI application package
for all supported platforms.
The system MUST use the bundled binary exclusively — it MUST NOT depend on any
system-installed `restic`.

#### Scenario: Fresh install, no system restic

- GIVEN a machine with no `restic` installed
- WHEN the user creates a backup from the GUI
- THEN the bundled restic executes successfully
- AND no error about missing restic is shown

### Requirement: Snapshot Repository Initialization

The system MUST initialize a restic repository the first time a backup is created.
The default repository path MUST be outside `~/reorder`:
- Windows: `C:\Users\{username}\reorder-backups`
- Linux/macOS: `~/.reorder-backups`
The user MUST be able to override the repository path in settings.
The repository MUST include both `~/reorder` file tree AND `reorder.db`.

#### Scenario: First backup on Linux

- GIVEN no backup repository exists
- WHEN the user clicks "Create Snapshot"
- THEN `restic init` is run at `~/.reorder-backups`
- AND `restic backup ~/reorder` captures files and database together

#### Scenario: User selects custom repository path

- GIVEN the user sets `/mnt/external-drive/reorder-backups` in settings
- WHEN a snapshot is created
- THEN restic uses the custom path as the repository

### Requirement: Snapshot Creation

The system MUST create incremental snapshots — only new or modified files
are stored after the first full snapshot.
The system MUST display progress during snapshot creation.
The system MUST tag each snapshot with the creation timestamp.

#### Scenario: Second snapshot after adding 100 new photos

- GIVEN a restic repository with one existing snapshot
- WHEN the user creates a new snapshot
- THEN only the 100 new files are written to the repository
- AND the snapshot completes significantly faster than the first

#### Scenario: Destination disk has insufficient space

- GIVEN the repository disk has less than 500MB free
- WHEN a snapshot is initiated
- THEN an error is shown: "Insufficient space at backup location"
- AND no partial snapshot is written

### Requirement: Snapshot Listing

The system MUST display a list of available snapshots with timestamp and
file count in the GUI.

#### Scenario: User opens backup history

- GIVEN 3 snapshots exist
- WHEN the user opens the backup panel
- THEN all 3 snapshots are listed with date, time, and file count

### Requirement: Full Restore

The system MUST restore the complete state of `~/reorder` and `reorder.db`
from a selected snapshot.
The system MUST require explicit confirmation before restoring, warning that
current state will be replaced.
The system MUST close the database connection before restore and reopen after.

#### Scenario: User restores to a previous snapshot

- GIVEN 3 snapshots exist and the user selects snapshot #2
- WHEN they confirm the restore
- THEN the GUI closes the database
- AND `restic restore` overwrites `~/reorder` with the snapshot contents
- AND the GUI reopens and reloads the file tree from the restored database

#### Scenario: User cancels restore

- GIVEN the confirmation dialog is shown
- WHEN the user clicks "Cancel"
- THEN no files are modified
