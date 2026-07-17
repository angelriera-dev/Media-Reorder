import argparse
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dates import get_photo_date
from search import find_images

def check_metadata(source_dir):
    print(f"{'Archivo':<40} | {'Fecha (Y-M-D)':<15} | {'Fuente'}")
    print("-" * 70)
    
    count = 0
    for filepath in find_images(source_dir):
        date_info = get_photo_date(filepath)
        filename = os.path.basename(filepath)
        
        if date_info:
            year, month, day, source = date_info
            print(f"{filename[:40]:<40} | {year}-{month:02d}-{day:02d} | {source}")
        else:
            print(f"{filename[:40]:<40} | {'?':<15} | {'?'}")
        count += 1
        
    print("-" * 70)
    print(f"Total procesados: {count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verifica metadatos de fotos")
    parser.add_argument("source_dir", nargs="?", default="test/src", help="Directorio a escanear (default: test/src)")
    args = parser.parse_args()
    
    check_metadata(args.source_dir)
