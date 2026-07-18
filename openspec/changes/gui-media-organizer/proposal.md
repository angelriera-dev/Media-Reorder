# Proposal: gui-media-organizer

## Intent

Evolve `reorder` from a single-purpose CLI photo organizer into a full-featured
desktop media organizer application. The Python package is the shared core and
ships on pip; the GUI shell is a Tauri app built on top of the same SQLite
database.

## Problem Statement

The current CLI tool handles one workflow: copy photos organized by date. Users
with large Google Photos / Google Drive exports need more: preview what they're
organizing, track what was copied, add context via tags, verify integrity with
backups, and handle Google's sidecar JSON metadata files. A CLI cannot provide
this experience without becoming unmaintainable.

## Scope

### In scope

- Monorepo: one repo, one `pyproject.toml`, CLI + GUI side by side
- Python package `reorder` published on pip — includes CLI entry point and all core logic
- Desktop GUI application (Tauri + Rust) distributed as `.exe` / `.dmg` / `.AppImage`
- GUI bundles: CPython standalone, `exiftool`, `restic` — zero user setup required
- SQLite database (`reorder.db`) as shared contract between CLI and GUI
- Media viewer: image and video preview
- File tree: cached history of copied files with source tracking and sibling navigation
- Custom reusable tags with XMP writeback via exiftool
- Delete-source option with SHA-256 integrity verification
- Google Drive JSON sidecar parsing
- Backup via bundled `restic` — reversible snapshots outside `~/reorder`
- Default output directory: `C:\Users\{user}\reorder` (Windows) / `~/reorder` (Linux/macOS)
- Performance: batch `exiftool` calls, metadata SQLite cache

### Out of scope

- Cloud sync / upload
- Face recognition or AI tagging
- Mobile companion app
- Multi-user / shared library

## Architecture Decision: Monorepo Structure

### One pyproject.toml

The Python package `reorder` IS the core. The CLI is an entry point within
the same package. No `core/` + `cli/` split — that separation only makes sense
when the two have independent release cycles or dependency profiles, which is
not the case here.

```
reorder/                        ← git root
├── pyproject.toml              ← one package: "reorder" on pip
├── reorder/                    ← Python package
│   ├── schema.py               ← SQLite schema (source of truth)
│   ├── db.py                   ← all SQL queries
│   ├── dates.py                ← metadata extraction
│   ├── search.py               ← file discovery
│   ├── organize.py             ← copy + verify
│   ├── sidecar.py              ← Google Drive JSON parser
│   └── cli.py                  ← argparse entry point
├── app/                        ← Tauri + Rust GUI
│   ├── src-tauri/
│   │   └── src/
│   │       ├── main.rs
│   │       ├── db.rs           ← reads reorder.db via rusqlite
│   │       └── commands.rs     ← invokes Python core for processing
│   └── src/                    ← HTML/CSS/JS frontend
├── schema/
│   └── schema.sql              ← generated from schema.py, embedded in Rust
└── tests/
```

### Schema as shared contract

`schema/schema.sql` is the API between Python and Rust.
- Python (`db.py`) executes it at runtime to create/migrate the database.
- Rust (`db.rs`) embeds it at compile time via `include_str!("../../schema/schema.sql")`.
- Any schema change requires updating `schema/CHANGELOG.md` with migration notes.

### Architecture Decision: Language

**Recommendation: Python CLI (pip) + Rust + Tauri (GUI)**

Rationale:
- Python CLI ships fast, reuses existing proven logic in `dates.py` / `organize.py`.
- The bottleneck is `exiftool` subprocess I/O, not Python interpreter speed.
- Media preview (image + video) is `<img>` and `<video>` in WebView — trivial in Tauri.
- Tauri produces a self-contained binary with no runtime dependency for end users.
- GUI bundles CPython standalone to invoke Python core without user installing Python.
- If Python core is later rewritten in Rust, the SQLite contract remains identical.

### Rejected alternatives

| Option | Reason rejected |
|--------|----------------|
| Two pyproject.toml (core + cli split) | No independent release cycles — premature separation |
| Python + Tkinter/PyQt6 | Video preview painful; large binary |
| Electron | ~200MB baseline; Tauri solves it at ~10MB |
| Go + Fyne | Immature GUI; limited video support |
| Full Rust rewrite from day one | Rewrites dates.py edge cases; blocks fast MVP |

## Delivery Phases

| Phase | Scope | Target users | Stack |
|-------|-------|-------------|-------|
| 0 | CLI + SQLite capture + batch exiftool + Google JSON | You + GitHub | Python |
| 1 | GUI shell + file tree + detail panel | GitHub community | Tauri |
| 2 | Media viewer + tags + XMP writeback | GitHub community | Tauri |
| 3 | Backup (restic) + delete source with SHA-256 | GitHub community | Tauri |
| 4 | Polish + installer wizard + onboarding | Non-technical users | Tauri |

**Phase 0 is critical:** if users delete source files before Phase 0 runs,
`source_path`, `source_parent_dir`, and Google JSON data are lost permanently.
All GUI features depend on this data existing in `reorder.db`.

## Capabilities

### New Capabilities

- `architecture` — Monorepo structure, schema contract, distribution model
- `media-viewer` — Preview images and videos inside the application
- `file-tree` — Cached history tree with detail panel, origin, and sibling navigation
- `tags` — Reusable user-defined tags with XMP writeback via exiftool
- `backup` — Reversible snapshots via bundled restic outside `~/reorder`
- `google-drive-import` — Parse `.json` sidecar files from Google Photos exports

### Modified Capabilities

- `file-discovery` — Batch exiftool, SQLite cache, Google Drive sidecar integration

## Rollback Plan

The existing `reorder.py` CLI entry point remains unchanged through Phase 0.
The GUI is an additive layer — removing `app/` leaves a fully functional CLI.
If Tauri is abandoned, the Python core can be wrapped in any other GUI framework
without touching `reorder/` package internals.

## Risks

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| User deletes source before Phase 0 runs | High | Document clearly: run CLI first, delete after |
| Rust learning curve blocks GUI delivery | Medium | Phase 0 delivers value without GUI |
| exiftool / restic not bundled correctly | Medium | Bundle both as app assets, test on clean VMs |
| Schema migration breaks existing DBs | Low | schema/CHANGELOG.md + migration scripts in db.py |
| Google Drive JSON format changes | Low | Schema version check on parse |
