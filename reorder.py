import argparse
from pathlib import Path

from organize import compress_backup, copy_photos, verify_copy

ORDER_DIR = "./order"


def main():
    parser = argparse.ArgumentParser(description="Organiza fotos por fecha")
    parser.add_argument(
        "source_dir",
        nargs="?",
        default="/respaldo",
        help="Carpeta a escanear (default: /respaldo)",
    )
    args = parser.parse_args()

    Path(ORDER_DIR).mkdir(parents=True, exist_ok=True)

    print(f"Escaneando {args.source_dir}...")
    copied = copy_photos(args.source_dir, ORDER_DIR)
    print(f"\n{len(copied)} archivos copiados a {ORDER_DIR}")

    print("\nVerificando integridad...")
    ok, missing, size_mismatch = verify_copy(copied)

    if ok:
        print(f"✓ Verificación exitosa: {len(copied)} archivos OK")
    else:
        if missing:
            print(f"✗ Archivos faltantes en destino ({len(missing)}):")
            for path in missing:
                print(f"  - {path}")
        if size_mismatch:
            print(f"✗ Archivos con tamaño diferente ({len(size_mismatch)}):")
            for src, src_size, dst, dst_size in size_mismatch:
                print(f"  - {src} ({src_size}B) → {dst} ({dst_size}B)")


if __name__ == "__main__":
    main()
