# Design: CLI Media Organizer

## Technical Approach

Restructure the flat Python scripts into a clean `reorder` module package. Define a database schema using SQLite, and implement database operations using the standard library `sqlite3` module. Wire up exiftool batch queries and Google Takeout JSON sidecar reading to parse metadata into the cache.

## Architecture Decisions

### Decision: Module Packaging
**Choice**: Package Python scripts under `reorder/` module directory.
**Alternatives considered**: Keep scripts flat in git root.
**Rationale**: Packaging makes the utility distributable via pip and allows cleaner relative imports.

### Decision: Dependency & Environment Manager
**Choice**: Use `uv` for package management and project setup.
**Alternatives considered**: standard `pip` + `venv`, `poetry`.
**Rationale**: `uv` provides extremely fast installs, a clean lockfile structure (`uv.lock`), and robust PEP 621 compliance.

### Decision: Metadata Cache Database
**Choice**: Use `sqlite3` in `reorder/db.py` to create a `reorder.db` database.
**Alternatives considered**: JSON file cache.
**Rationale**: SQLite handles concurrent reads, query filtering, and scales better for large photo libraries.

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `reorder/schema.py` | Create | Database schema generation script |
| `reorder/db.py` | Create | Database connection, initialization, and CRUD queries |
| `reorder/sidecar.py` | Create | Google Takeout `.json` sidecar parser |
| `reorder/cli.py` | Create | Command-line entry point parsing arguments |
| `reorder/dates.py` | Modify | Integrate metadata caching and Google sidecar waterfall fallbacks |
| `reorder/search.py` | Modify | Video and photo discovery with sidecar checks |
| `reorder/organize.py` | Modify | Wire up sqlite3 tracking for copying files |

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | DB queries, sidecar parser | Standard `unittest` with mock file contents |
| Integration | organize workflow | End-to-end dry run with test source directory |
