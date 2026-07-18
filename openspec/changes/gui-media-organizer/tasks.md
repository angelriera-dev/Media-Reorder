# Tasks: GUI Media Organizer

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 1200–1800 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 (Tauri shell) → PR 2 (features + cleanup) |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Tauri scaffold + file tree + detail panel + media viewer | PR 1 | `cargo test` in `app/src-tauri/` | Launch app, verify file tree | Remove `app/` directory |
| 2 | Tags + backup + delete-source + cleanup | PR 2 | `cargo test` | Assign tag in GUI, create/restore snapshot | Revert additions in commands.rs |

## Phase 3: GUI Shell — Tauri

- [ ] 3.1 RED: `tests/test_bundled_binary.py::test_bundled_binary_path_resolution` — assert bundled path used, not PATH
- [ ] 3.2 RED: `tests/test_backup.py::test_backup_repo_not_inside_output` — assert repo path outside `~/reorder`
- [ ] 3.3 Implement CLI-compatible path resolution in GUI (mandatory source, dynamic target)
- [ ] 3.4 Implement SHA256-based deduplication check via `copy_history`
- [ ] 3.5 Scaffold `app/src-tauri/` — `Cargo.toml` (tauri + rusqlite), `tauri.conf.json`, `src/main.rs`
- [ ] 3.6 Create `app/src-tauri/src/db.rs` — `include_str!` schema embed, `list_history`, `get_file_detail` queries
- [ ] 3.7 Create `app/src-tauri/src/commands.rs` — IPC: `list_history`, `get_file_detail`, `assign_tag`, `delete_source`, `create_snapshot`, `restore_snapshot`
- [ ] 3.8 Create `app/src/index.html` + JS — file tree panel, detail panel, `<img>`/`<video>` media viewer

## Phase 4: Cleanup

- [ ] 4.1 Delete root scripts `reorder.py`, `organize.py`, `dates.py`, `search.py` after core package verified
- [ ] 4.2 Create `schema/CHANGELOG.md` with v1 entry
