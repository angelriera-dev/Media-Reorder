# Tasks: CLI Media Organizer

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 800–1200 |
| 400-line budget risk | Medium |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Medium

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Python package + schema + sidecar + batch exiftool + CLI | PR 1 | `python -m unittest discover tests/` | `python -m reorder.cli /tmp/test-src /tmp/test-dest` | Revert `reorder/` package, restore root scripts |

## Phase 1: Foundation — Schema + Database

- [x] 1.1 Create `schema/schema.sql` — DDL for `copy_history`, `metadata_cache`, `tags`, `file_tags`
- [x] 1.2 Create `reorder/__init__.py` + `reorder/db.py` — init schema from `schema.sql`, CRUD for tables
- [x] 1.3 Create `reorder/sidecar.py` — parse `{file}.json` Google Takeout sidecars

## Phase 2: Core Engine — Security Tests & CLI Refactoring

- [x] 2.1 RED: `tests/test_security.py::test_invalid_source_path` — assert error on `../../etc/passwd`
- [x] 2.2 RED: `tests/test_security.py::test_path_with_shell_metachar` — assert subprocess gets literal path, no `shell=True`
- [x] 2.3 RED: `tests/test_security.py::test_delete_blocked_on_hash_mismatch` — assert delete blocked when SHA-256 differs
- [x] 2.4 Move `dates.py` → `reorder/dates.py`; add batch exiftool, metadata cache lookup, sidecar fallback
- [x] 2.5 Move `search.py` → `reorder/search.py`; add video extensions + sidecar discovery
- [x] 2.6 Move `organize.py` → `reorder/organize.py`; wire `db.py` for copy history writes + SHA-256 validation
- [x] 2.7 Create `reorder/cli.py` from `reorder.py`; update `pyproject.toml` `[project.scripts]`
- [x] 2.8 Rename `test/` → `tests/` (done); add `tests/test_sidecar.py`, `tests/test_db.py`, `tests/test_dates.py`
