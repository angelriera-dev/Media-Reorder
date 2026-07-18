# Architecture Specification (GUI)

## Purpose

Define the Tauri GUI structure, Rust commands bridge, embedded binaries, and delivery phases.

## Requirements

### Requirement: Tauri Project Structure

The desktop application is built using Tauri.

```
reorder/
├── app/                        ← Tauri + Rust GUI
│   ├── src-tauri/
│   │   └── src/
│   │       ├── main.rs
│   │       ├── db.rs           ← rusqlite integration
│   │       └── commands.rs     ← tauri command handlers
│   └── src/                    ← HTML/CSS/JS frontend
```

### Requirement: Bundling Binaries

The desktop GUI application MUST bundle `exiftool` and `restic` sidecars. The application must invoke them using Tauri's Sidecar API.

### Requirement: Commands IPC Bridge

The application MUST define Tauri IPC commands for interacting with the database and executing core workflows:
- `list_history`
- `get_file_detail`
- `assign_tag`
- `delete_source`
- `create_snapshot`
- `restore_snapshot`
