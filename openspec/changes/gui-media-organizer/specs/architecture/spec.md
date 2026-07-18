# Architecture Specification

## Purpose

Define the monorepo structure, distribution model, schema contract, and
delivery phases for the reorder project.

## Requirements

### Requirement: Monorepo Structure

The project MUST live in a single git repository with one `pyproject.toml`.
The Python package and the Tauri GUI MUST coexist in the same repo.
The repo MUST NOT be split into separate packages until independent release
cycles or dependency profiles justify it.

```
reorder/                        ← git root
├── pyproject.toml              ← one package: "reorder" on pip
├── reorder/                    ← Python package (core + CLI)
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
│   │       ├── db.rs
│   │       └── commands.rs
│   └── src/                    ← HTML/CSS/JS frontend
├── schema/
│   ├── schema.sql              ← generated from schema.py, embedded in Rust
│   └── CHANGELOG.md            ← migration notes per schema version
└── tests/
```

#### Scenario: Developer adds a new field to the schema

- GIVEN a new field is needed in the database
- WHEN the developer updates `schema/schema.sql`
- THEN `schema/CHANGELOG.md` is updated with migration notes
- AND `reorder/db.py` handles the migration at runtime (ALTER TABLE or recreate)
- AND `app/src-tauri/src/db.rs` picks up the new schema at next compile via `include_str!`

### Requirement: Schema as Shared Contract

`schema/schema.sql` MUST be the single source of truth for the database structure.
Python MUST execute it at runtime to create or migrate `reorder.db`.
Rust MUST embed it at compile time via `include_str!("../../schema/schema.sql")`.
No hardcoded CREATE TABLE statements are allowed outside `schema/schema.sql`.

#### Scenario: Fresh install, CLI run

- GIVEN a machine with no `reorder.db`
- WHEN the user runs `reorder /source/dir`
- THEN `db.py` executes `schema.sql` and creates `reorder.db` at the default path
- AND the organize run populates the database

#### Scenario: GUI opens existing database from CLI run

- GIVEN `reorder.db` was created by the CLI in a previous session
- WHEN the GUI launches
- THEN `db.rs` opens the same `reorder.db` without migration errors
- AND all file history is visible in the file tree immediately

### Requirement: CLI Distribution via pip

The Python package `reorder` MUST be published on PyPI.
The CLI entry point MUST be declared in `pyproject.toml` as:
`reorder = "reorder.cli:main"`
Installing via `pip install reorder` MUST make the `reorder` command available.

#### Scenario: Technical user installs CLI

- GIVEN a machine with Python 3.13+
- WHEN the user runs `pip install reorder`
- THEN `reorder --help` works from the terminal
- AND running `reorder /source /dest` organizes files and writes `reorder.db`

### Requirement: GUI Distribution as Native Binary

The GUI MUST be distributed as a self-contained binary per platform:
- Windows: `.exe` installer
- macOS: `.dmg`
- Linux: `.AppImage`

The GUI binary MUST bundle:
- CPython standalone (to invoke Python core without user installing Python)
- `exiftool` binary
- `restic` binary

The user MUST NOT need to install Python, exiftool, or restic manually.

#### Scenario: Non-technical user installs GUI on Windows

- GIVEN a clean Windows machine with no Python or exiftool installed
- WHEN the user runs the `.exe` installer
- THEN the app launches and organizes files without any additional setup

#### Scenario: GUI and CLI coexist on same machine

- GIVEN a developer has both `pip install reorder` and the GUI app installed
- WHEN the CLI writes to `~/reorder/reorder.db`
- THEN the GUI opens the same database and shows the full history

### Requirement: Delivery Phase Sequencing

The system MUST be delivered in phases. Phase 0 MUST ship before any user
deletes source files, as all GUI features depend on data captured in Phase 0.

| Phase | Scope | Stack |
|-------|-------|-------|
| 0 | CLI + SQLite + batch exiftool + Google JSON sidecar | Python |
| 1 | GUI shell + file tree + detail panel | Tauri |
| 2 | Media viewer + tags + XMP writeback | Tauri |
| 3 | Backup (restic) + delete source (SHA-256) | Tauri |
| 4 | Installer wizard + onboarding for non-technical users | Tauri |

#### Scenario: User deletes source before Phase 0

- GIVEN a user organized files with the current CLI (pre-Phase 0)
- WHEN they delete source files
- THEN `source_path`, `source_parent_dir`, and Google JSON data are permanently lost
- AND GUI features (origin panel, siblings, sidecar metadata) will be unavailable for those files

#### Scenario: User runs Phase 0 CLI then opens Phase 1 GUI

- GIVEN Phase 0 has populated `reorder.db` with full history
- WHEN the user opens the GUI for the first time
- THEN all previously organized files appear in the file tree with full metadata
- AND no re-processing of source files is required
