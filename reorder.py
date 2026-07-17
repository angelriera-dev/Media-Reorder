import argparse
from pathlib import Path

from organize import compress_backup, copy_photos

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
    count = copy_photos(args.source_dir, ORDER_DIR)
    print(f"\n{count} archivos copiados a {ORDER_DIR}")

    # print("\n¿Deseas comprimir? (S/n)")
    # if input().lower() != "n":
    #     compress_backup(args.source_dir, "./respaldo_comprimido")


if __name__ == "__main__":
    main()
