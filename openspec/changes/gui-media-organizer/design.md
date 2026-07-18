# Design: GUI Media Organizer

## Technical Approach

Build a desktop GUI application using Tauri + Rust + Svelte/HTML5. Define IPC commands in Rust to read database tables from SQLite and interface with the metadata tags and restic backup commands.

## Architecture Decisions

### Decision: CLI Compatibility
**Choice**: GUI must enforce identical argument structure as CLI (mandatory source, dynamic output path).
**Rationale**: Consistency of user experience between modes.

### Decision: Content-Based Deduplication
**Choice**: GUI will query `copy_history` SHA256 column before initiating copies.
**Rationale**: Prevent redundant storage of identical files identified by content hash, not just path.

### Decision: Tauri Framework
**Choice**: Use Tauri with Rust backend and HTML5 frontend.
**Alternatives considered**: PyQt6, Electron.
**Rationale**: Tauri keeps the binary footprint extremely small and uses the OS webview, avoiding the overhead of bundling Chromium.

### Decision: IPC Bridge
**Choice**: Custom Tauri commands in Rust mapping to SQLite queries.
**Alternatives considered**: Direct SQLite calls from frontend JS.
**Rationale**: Security and performance: Javascript in webview should not open database connections directly.

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `app/src-tauri/Cargo.toml` | Create | Rust dependencies configuration |
| `app/src-tauri/src/main.rs` | Create | App initialization and setup |
| `app/src-tauri/src/db.rs` | Create | Read reorder.db tables using rusqlite |
| `app/src-tauri/src/commands.rs` | Create | Tauri IPC command handlers |
| `app/src/index.html` | Create | Frontend entry point |

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | Rust commands & DB integration | `cargo test` inside `app/src-tauri` |
| Integration | IPC messages, frontend views | Mock Tauri invoke methods in JS tests |
