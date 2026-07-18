# Proposal: cli-media-organizer

## Intent

Evolve `reorder` from a single-purpose CLI photo organizer into a modular command-line interface application. The Python package acts as the core library, incorporating a sqlite database to track history and cache metadata.

## Problem Statement

The current CLI tool handles one workflow: copy photos organized by date. Users with large Google Photos / Google Drive exports need metadata caching, duplicate prevention, Google Takeout sidecar JSON parsing, and a reliable database layer to capture historical copy actions.

## Scope

### In scope

- Python package `reorder` published on PyPI.
- SQLite database (`reorder.db`) containing copy history and metadata cache.
- Google Takeout JSON sidecar file parsing.
- Batch exiftool invocation (`exiftool -json <dir>`) with SQLite caching.
- Validation of source paths and shell injection mitigation.

### Out of scope

- Tauri GUI application or graphical interfaces.
- Backup snapshots via restic.
- GUI installer wizards.

## Architecture Decisions

### Schema as shared contract

`schema/schema.sql` is the database source of truth.
- Python (`db.py`) executes it at runtime to create/migrate the database.
- Any schema change requires updating `schema/CHANGELOG.md` with migration notes.

### Python CLI Distribution via pip and uv

The Python package `reorder` is published on PyPI. The CLI entry point is defined in `pyproject.toml` as `reorder = "reorder.cli:main"`. Dependency and virtual environment management is handled via `uv`.

## Delivery Phases

| Phase | Scope | Stack |
|-------|-------|-------|
| 0 | CLI + SQLite capture + batch exiftool + Google JSON sidecar | Python |

## Capabilities

### New Capabilities

- `architecture` — Python package structure, database schema, CLI entry points
- `google-drive-import` — Parse `.json` sidecar files from Google Photos exports

### Modified Capabilities

- `file-discovery` — Batch exiftool, SQLite cache, Google Drive sidecar integration
