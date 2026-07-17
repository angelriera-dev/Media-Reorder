import os
import shutil
import subprocess
from pathlib import Path

from dates import get_date, format_date
from search import find_images


def copy_photos(source_dir, output_dir):
    """Copy images from source_dir into output_dir organized by date."""
    file_count = 0

    for filepath in find_images(source_dir):
        filename = os.path.basename(filepath)
        date = get_date(filepath)

        if not date:
            print(f"⚠ No se pudo determinar fecha para: {filename}")
            continue

        day_str, month_name = format_date(*date)
        if not day_str:
            continue

        year = date[0]
        month = date[1]
        target_dir = os.path.join(
            output_dir, str(year), f"{month:02d}-{month_name}", day_str
        )
        Path(target_dir).mkdir(parents=True, exist_ok=True)

        target_path = os.path.join(target_dir, filename)
        if os.path.exists(target_path):
            name, ext = os.path.splitext(filename)
            target_path = os.path.join(target_dir, f"{name}_dup{file_count}{ext}")

        try:
            shutil.copy2(filepath, target_path)
            file_count += 1
            print(f"✓ Copiado: {filename} → {target_dir}")
        except Exception as e:
            print(f"✗ Error copiando {filename}: {e}")

    return file_count


def compress_backup(source_dir, output_dir):
    """Compress source_dir into a tar.gz."""
    print(f"\nComprimiendo {source_dir}...")
    try:
        subprocess.run(
            [
                "tar", "-czf", f"{output_dir}/backup.tar.gz",
                "-C", os.path.dirname(source_dir), os.path.basename(source_dir),
            ],
            check=True,
        )
        print(f"✓ Comprimido en: {output_dir}/backup.tar.gz")
    except Exception as e:
        print(f"✗ Error comprimiendo: {e}")
