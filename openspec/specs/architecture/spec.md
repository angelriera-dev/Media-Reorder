# Architecture Specification (CLI)

## Purpose

Define the package structure, distribution model, schema contract, and delivery phases for the CLI core of the reorder project.

## Requirements

### Requirement: Package Structure

The project lives in a single git repository with one `pyproject.toml`.

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
├── schema/
│   ├── schema.sql              ← generated from schema.py
│   └── CHANGELOG.md            ← migration notes per schema version
└── tests/
```

### Requirement: Schema as Contract

`schema/schema.sql` MUST be the single source of truth for the database structure.
Python MUST execute it at runtime to create or migrate `reorder.db`.

### Requirement: CLI Distribution via pip

The Python package `reorder` MUST be published on PyPI.
The CLI entry point MUST be declared in `pyproject.toml` as:
`reorder = "reorder.cli:main"`
Installing via `pip install reorder` MUST make the `reorder` command available.

### Requirement: Development and Dependency Management via uv

The project MUST use `uv` for package configuration, virtual environments, and dependency resolution. The `uv.lock` file MUST be maintained as the lockfile source of truth.