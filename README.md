# Multimedia Backup Organizer

A modular Python utility to automatically organize, classify, and compress multimedia files into a date-based structure using advanced metadata extraction.

## Features

- ✅ **Modular Architecture**: Clean separation of concerns (`dates`, `search`, `organize`).
- ✅ **Advanced Metadata Extraction**: Uses `exiftool` (high-priority) with multiple fallback strategies (binary XMP, filename patterns, filesystem mtime).
- ✅ **Robust Date Detection**: Handles complex EXIF structures, XMP, IPTC, and varied date formats.
- ✅ **CLI-First**: Specify source directories via command line arguments.
- ✅ **Diagnostics**: Includes a `test/get_meta.py` utility for inspecting file metadata extraction paths.

## Installation

### Requirements

- Python 3.10+
- `exiftool` (mandatory for accurate date extraction)

```bash
# Ubuntu/Debian
sudo apt-get install libimage-exiftool-perl

# macOS
brew install exiftool
```

### Setup

1. **Install dependencies**:
   ```bash
   uv sync
   ```

## Usage

### Organize Photos

Run the main script providing the source directory:

```bash
# Using default (/respaldo)
python reorder.py

# With custom directory
python reorder.py ~/pCloudDrive/Finanzas/Fotos
```

### Diagnostics

Verify how the metadata extraction is performing on a specific set of files:

```bash
# Checks test/src/ by default
python test/get_meta.py

# Check a specific directory
python test/get_meta.py ~/pCloudDrive/Finanzas/Fotos
```

## Modular Structure

- `reorder.py`: Entry point and CLI parsing.
- `search.py`: Recursive file discovery.
- `dates.py`: Centralized metadata extraction logic (the core engine).
- `organize.py`: File copy operations and compression routines.
- `test/get_meta.py`: Debugging utility for metadata extraction verification.

---
**Happy organizing!** 📸✨
