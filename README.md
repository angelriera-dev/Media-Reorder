# Multimedia Backup Organizer

A Python utility to automatically organize, classify, and compress multimedia files from a backup directory into a date-based folder structure.

## Overview

This project solves the problem of managing large, unorganized backup directories containing thousands of photos nested in multiple folder levels. It:

1. **Recursively scans** a source backup directory (`/respaldo`) for all media files
2. **Extracts dates** from file metadata, filenames, or modification timestamps
3. **Organizes files** into a hierarchical date-based structure (`/order/YYYY/MM-Mon/DDth-Day/`)
4. **Compresses** the original backup directory to save disk space

## Features

- ✅ **Recursive file discovery** - Finds images at any folder depth
- ✅ **Smart date extraction** - Uses metadata → filename → modification date priority
- ✅ **EXIF metadata parsing** - Extracts DateTimeOriginal from photos
- ✅ **Pattern matching** - Recognizes common date formats (YYYYMMDD, YYYY-MM-DD, etc.)
- ✅ **Organized output** - Year/Month/Day folder hierarchy with day-of-week labels
- ✅ **Duplicate handling** - Prevents file overwrites with automatic suffixing
- ✅ **Compression ready** - One-command tar.gz backup creation
- ✅ **Progress tracking** - Real-time console output of processed files

## Installation

### Requirements

- Python 3.7+
- `exiftool` (for EXIF metadata extraction)

### Setup

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install python3 exiftool
```

#### macOS
```bash
brew install exiftool
```

#### Windows
Download `exiftool.exe` from [exiftool.org](https://exiftool.org/) and add to PATH, or install via:
```bash
choco install exiftool
```

## Usage

### Basic Usage

1. **Clone or download** the script:
```bash
git clone <repository-url>
cd multimedia-organizer
```

2. **Configure paths** (edit the script):
```python
SOURCE_DIR = "/respaldo"          # Your backup directory
ORDER_DIR = "/order"              # Output directory
BACKUP_DIR = "/respaldo_comprimido"  # Compressed backup location
```

3. **Run the script**:
```bash
python3 organize_photos.py
```

4. **Compress the backup** (when prompted):
```
Compressing /respaldo...
✓ Compressed successfully to: /respaldo_comprimido/respaldo_backup.tar.gz
```

### Output Structure

Your files will be organized as:

```
/order/
├── 2026/
│   ├── 04-Apr/
│   │   ├── 15-Sun/
│   │   │   ├── photo_001.jpg
│   │   │   ├── photo_002.jpg
│   │   │   └── ...
│   │   └── 16-Mon/
│   │       └── photo_003.jpg
│   └── 05-May/
│       └── ...
├── 2025/
│   └── ...
```

## How It Works

### Date Detection Priority

The script attempts to extract dates in this order:

1. **EXIF Metadata** - `DateTimeOriginal` from photo metadata (most reliable)
2. **Filename Patterns** - Common formats:
   - `YYYYMMDD` (20260415)
   - `YYYY-MM-DD` (2026-04-15)
   - `YYYY_MM_DD` (2026_04_15)
3. **File Modification Date** - Last resort fallback

### Supported Image Formats

- `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`
- `.heic`, `.raw`, `.dng` (and other common formats)

## Configuration

Edit these variables in the script:

```python
SOURCE_DIR = "/respaldo"              # Source backup directory
ORDER_DIR = "/order"                  # Target organized directory
BACKUP_DIR = "/respaldo_comprimido"   # Where to store compressed backup
```

### Customize Image Extensions

Modify the `image_extensions` set in the `organize_photos()` function:

```python
image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.heic', '.raw', '.dng'}
```

## Examples

### Example 1: Organizing Phone Photos

**Input:**
```
/respaldo/
├── Camera/
│   └── IMG_20260415_143022.jpg
├── Backup_2026/
│   ├── old_backups/
│   │   └── 20260510_vacation.jpg
│   └── recent/
│       └── 2026-04-20_family.jpg
```

**Output:**
```
/order/
├── 2026/
│   ├── 04-Apr/
│   │   └── 15-Sun/
│   │       └── IMG_20260415_143022.jpg
│   ├── 05-May/
│   │   └── 10-Fri/
│   │       └── 20260510_vacation.jpg
│   └── 04-Apr/
│       └── 20-Fri/
│           └── 2026-04-20_family.jpg
```

## Troubleshooting

### Issue: "exiftool not found"

**Solution:** Install exiftool:
```bash
# Ubuntu/Debian
sudo apt-get install exiftool

# macOS
brew install exiftool

# Windows
choco install exiftool
```

### Issue: Date not detected for some files

The script will:
1. Fall back to file modification date (printed as ⚠ warning)
2. Still organize the file based on available information
3. Print warnings for unorganizable files

Example warning output:
```
⚠ Could not determine date for: old_photo.jpg
```

### Issue: Duplicate filenames in same day folder

The script automatically appends `_dup{number}` to prevent overwrites:
```
photo.jpg
photo_dup0.jpg
photo_dup1.jpg
```

### Issue: Permission denied errors

**Solution:** Check folder permissions:
```bash
chmod -R 755 /respaldo
chmod -R 755 /order
```

## Performance Tips

- **Large backups** (100k+ files): Run on a fast SSD for better performance
- **Network drives**: Copy to local disk first, then organize
- **Compression**: Use `tar -czf` for maximum compression or `tar -cf` for speed

## Advanced Usage

### Run from command line with custom paths

```bash
python3 organize_photos.py --source /media/backup --output /organized
```

(To implement, add argument parsing to the script)

### Dry run (preview changes)

Modify the script to use `shutil.copy2` → `print(f"Would copy: {filepath}")` for a dry run.

### Parallel processing

For very large backups, consider using Python's `multiprocessing` module:

```python
from multiprocessing import Pool

with Pool(processes=4) as pool:
    pool.map(process_file, file_list)
```

## Alternative: Bash/Shell Script Version

For a lightweight shell-only solution without Python dependencies:

```bash
#!/bin/bash
SOURCE="/respaldo"
TARGET="/order"

find "$SOURCE" -type f \( -iname "*.jpg" -o -iname "*.png" \) | while read file; do
    DATE=$(exiftool -DateTimeOriginal -d "%Y/%m-%b/%d-%a" "$file" | grep -oP '\d{4}/\d{2}-\w+/\d{2}-\w+')
    [ ! -z "$DATE" ] && mkdir -p "$TARGET/$DATE" && cp "$file" "$TARGET/$DATE/"
done

tar -czf /respaldo_backup.tar.gz /respaldo/
```

## License

MIT License - Free to use and modify

## Contributing

Contributions welcome! Areas for improvement:

- [ ] Video file support
- [ ] GUI interface
- [ ] Parallel processing for large backups
- [ ] Database integration for duplicate detection
- [ ] Cloud backup support (AWS S3, Google Drive, etc.)

## Support

For issues or questions:

1. Check the **Troubleshooting** section above
2. Review exiftool documentation: https://exiftool.org/
3. Open an issue on the repository

## Changelog

### v1.0.0 (Initial Release)
- Core photo organization functionality
- EXIF metadata extraction
- Filename pattern matching
- Compression support
- Cross-platform compatibility

---

**Happy organizing!** 📸✨
