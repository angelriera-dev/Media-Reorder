# Proposal: gui-media-organizer

## Intent

Implement a desktop graphical user interface (GUI) application for `reorder` using Tauri and Rust. The GUI shell embeds the Python core library and coordinates the database layer.

## Problem Statement

Users of the command-line interface need a graphical way to view and manage media. A desktop application allows them to preview images and videos, search the copy history tree, manage reusable metadata tags (with XMP writeback), and run backup snapshots via `restic`.

## Scope

### In scope

- Desktop GUI application (Tauri + Rust) distributed as native packages.
- GUI bundles containing CPython standalone, `exiftool`, and `restic`.
- Media viewer: image and video preview panel in HTML5/JS.
- File tree navigation representing `reorder.db` copy history.
- Custom tag library interface with exiftool XMP writeback.
- Backup configuration running restic snapshots.

### Out of scope

- Direct database schema design (reuses contract schema from CLI).
- Publishing python package to PyPI (responsibility of CLI/core).

## Architecture Decisions

### Bundling binaries

The Tauri application bundles its dependencies (CPython, exiftool, restic) so the end user does not need separate installations.

### Commands IPC bridge

Rust handles UI queries, reads from SQLite via rusqlite, and executes Python CLI tasks via subprocess commands when required.

## Delivery Phases

| Phase | Scope | Stack |
|-------|-------|-------|
| 1 | GUI shell + file tree + detail panel | Tauri + Rust |
| 2 | Media viewer + tags + XMP writeback | Tauri + Rust |
| 3 | Backup (restic) + delete source (SHA-256) | Tauri + Rust |
| 4 | Polish + installer wizard + onboarding | Tauri + Rust |

## Capabilities

- `media-viewer` — Preview images and videos
- `file-tree` — Navigation tree with origin/detail panel
- `tags` — Tagging panel with exiftool integration
- `backup` — restic snapshots control
