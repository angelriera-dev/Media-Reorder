"""CLI entry point for reorder."""
import argparse
from pathlib import Path

from .db import get_db
from .organize import copy_photos, validate_source_path, verify_copy


def main():
    parser = argparse.ArgumentParser(description="Organize photos by date")
    parser.add_argument(
        "source_dir",
        nargs="?",
        default="/respaldo",
        help="Directory to scan (default: /respaldo)",
    )
    parser.add_argument(
        "-o", "--output",
        default="./order",
        help="Output directory (default: ./order)",
    )
    args = parser.parse_args()

    try:
        source = validate_source_path(args.source_dir)
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    # Default output dir
    output_dir = Path(args.output).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # DB in target dir
    db_path = output_dir / "reorder.db"
    conn = get_db(db_path)
    
    print(f"Scanning {source}...")
    copied = copy_photos(source, str(output_dir), conn=conn)
    print(f"\n{len(copied)} files copied to {args.output}")

    print("\nVerifying integrity...")
    ok, missing, size_mismatch = verify_copy(copied)

    if ok:
        print(f"Verification OK: {len(copied)} files verified")
    else:
        if missing:
            print(f"Missing files ({len(missing)}):")
            for path in missing:
                print(f"  - {path}")
        if size_mismatch:
            print(f"Size mismatches ({len(size_mismatch)}):")
            for src, src_size, dst, dst_size in size_mismatch:
                print(f"  - {src} ({src_size}B) -> {dst} ({dst_size}B)")

    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
