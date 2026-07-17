import subprocess
import re
from pathlib import Path
from datetime import datetime

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


# ──────────────────────────────────────────────
# 1. EXIF: búsqueda exhaustiva con exiftool
# ──────────────────────────────────────────────
def _from_metadata(filepath):
    """
    Extrae fecha usando exiftool buscando en TODAS las etiquetas
    de fecha disponibles, con orden de prioridad.
    """
    # Prioridad de etiquetas: de más confiable a menos
    PRIORITY_TAGS = [
        # EXIF estándar
        "DateTimeOriginal",
        "CreateDate",
        "ModifyDate",
        # XMP
        "XMP:DateCreated",
        "XMP:CreateDate",
        "XMP:DateTimeOriginal",
        "XMP:MetadataDate",
        "XMP:ModifyDate",
        # IPTC
        "IPTC:DateCreated",
        "IPTC:DigitalCreationDate",
        # Otros
        "MediaCreateDate",
        "TrackCreateDate",
        "GPSDateStamp",
        "ProfileDateTime",
        "FileModifyDate",  # último recurso (≈ mtime)
    ]

    # Estrategia 1: pedir tags específicos
    cmd = ["exiftool", "-S", "-s"] + [f"-{tag}" for tag in PRIORITY_TAGS] + [filepath]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        for line in result.stdout.splitlines():
            date = _parse_date_string(line)
            if date:
                print(f"  [EXIF tag match]: {line.strip()} → {date}")
                return date
    except Exception as e:
        print(f"  [EXIF error]: {e}")

    # Estrategia 2: buscar CUALQUIER campo con fecha en todo el metadata
    cmd_all = ["exiftool", "-a", "-G1", "-s", "-time:all", filepath]
    try:
        result = subprocess.run(cmd_all, capture_output=True, text=True, timeout=5)
        if result.stdout.strip():
            print(f"  [EXIF all dates]:")
            for line in result.stdout.splitlines():
                print(f"    {line.strip()}")
            # Tomar la primera fecha válida
            for line in result.stdout.splitlines():
                date = _parse_date_string(line)
                if date and _is_reasonable_date(date):
                    print(f"  [EXIF fallback match]: {line.strip()} → {date}")
                    return date
    except Exception as e:
        print(f"  [EXIF all-dates error]: {e}")

    return None


def _parse_date_string(text):
    """Intenta extraer (year, month, day) de múltiples formatos de fecha."""
    patterns = [
        r"(\d{4}):(\d{2}):(\d{2})",  # 2024:03:15
        r"(\d{4})-(\d{2})-(\d{2})",  # 2024-03-15
        r"(\d{4})/(\d{2})/(\d{2})",  # 2024/03/15
        r"(\d{2})/(\d{2})/(\d{4})",  # 15/03/2024 → reordenar
    ]
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, text)
        if match:
            groups = list(map(int, match.groups()))
            if i == 3:  # formato DD/MM/YYYY
                groups = [groups[2], groups[1], groups[0]]
            return tuple(groups[:3])
    return None


def _is_reasonable_date(date_tuple):
    """Filtra fechas absurdas (futuras, muy antiguas, epoch)."""
    y, m, d = date_tuple
    now = datetime.now()
    if y < 1990 or y > now.year:
        return False
    if m < 1 or m > 12 or d < 1 or d > 31:
        return False
    # Evitar fechas epoch (1970-01-01)
    if y == 1970 and m == 1 and d == 1:
        return False
    return True


# ──────────────────────────────────────────────
# 2. JPEG binario: leer EXIF sin exiftool
# ──────────────────────────────────────────────
def _from_jpeg_binary(filepath):
    """
    Lee directamente los bytes del JPEG buscando
    cadenas de fecha en segmentos EXIF/XMP embebidos.
    Útil cuando exiftool no está instalado o falla.
    """
    try:
        with open(filepath, "rb") as f:
            data = f.read(65536)  # primeros 64KB (EXIF suele estar aquí)

        # Buscar patrones de fecha en los bytes crudos
        text = data.decode("latin-1", errors="ignore")
        # Buscar fechas tipo "2024:03:15 14:30:00"
        match = re.search(r"(\d{4}):([01]\d):([0-3]\d) \d{2}:\d{2}:\d{2}", text)
        if match:
            date = tuple(map(int, match.groups()))
            if _is_reasonable_date(date):
                print(f"  [Binary EXIF match]: {match.group()} → {date}")
                return date

        # Buscar en bloque XMP embebido (XML dentro del JPEG)
        xmp_start = text.find("<x:xmpmeta")
        if xmp_start != -1:
            xmp_end = text.find("</x:xmpmeta>", xmp_start)
            xmp_block = (
                text[xmp_start : xmp_end + 20]
                if xmp_end != -1
                else text[xmp_start : xmp_start + 4096]
            )
            for pattern in [r"(\d{4})-(\d{2})-(\d{2})T", r"(\d{4}):(\d{2}):(\d{2})"]:
                match = re.search(pattern, xmp_block)
                if match:
                    date = tuple(map(int, match.groups()))
                    if _is_reasonable_date(date):
                        print(f"  [XMP binary match]: {match.group()} → {date}")
                        return date
    except Exception as e:
        print(f"  [Binary read error]: {e}")
    return None


# ──────────────────────────────────────────────
# 3. Nombre de archivo (mejorado)
# ──────────────────────────────────────────────
def _from_filename(filepath):
    """Extrae fecha del nombre del archivo con múltiples patrones."""
    name = Path(filepath).stem
    patterns = [
        # IMG_20240315_143000, VID_20240315_143000
        r"(?:IMG|VID|PXL|MVIMG|SAVE|Screenshot)[_-](\d{4})(\d{2})(\d{2})",
        # WhatsApp Image 2024-03-15
        r"(\d{4})-(\d{2})-(\d{2})",
        # 20240315_143000 o 20240315-143000
        r"^(\d{4})(\d{2})(\d{2})[_\-]",
        # photo_2024-03-15
        r"photo[_-](\d{4})-(\d{2})-(\d{2})",
        # Signal-2024-03-15
        r"Signal[_-](\d{4})-(\d{2})-(\d{2})",
        # Timestamp Unix en el nombre (13 dígitos)
        # Se maneja aparte
    ]
    for pattern in patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            date = tuple(map(int, match.groups()))
            if _is_reasonable_date(date):
                return date

    # Intentar timestamp Unix en el nombre
    ts_match = re.search(r"(\d{13})", name)
    if ts_match:
        try:
            ts = int(ts_match.group(1)) / 1000
            dt = datetime.fromtimestamp(ts)
            date = (dt.year, dt.month, dt.day)
            if _is_reasonable_date(date):
                return date
        except (ValueError, OSError):
            pass

    return None


# ──────────────────────────────────────────────
# 4. Pillow fallback (sin exiftool)
# ──────────────────────────────────────────────
def _from_pillow(filepath):
    """Usa Pillow como alternativa a exiftool."""
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS

        img = Image.open(filepath)
        exif_data = img._getexif()
        if not exif_data:
            return None

        # Tags numéricos de interés
        DATE_TAG_IDS = {
            36867: "DateTimeOriginal",
            36868: "DateTimeDigitized",
            306: "DateTime",
        }
        for tag_id, tag_name in DATE_TAG_IDS.items():
            if tag_id in exif_data:
                date = _parse_date_string(str(exif_data[tag_id]))
                if date and _is_reasonable_date(date):
                    print(f"  [Pillow {tag_name}]: {exif_data[tag_id]} → {date}")
                    return date
    except ImportError:
        pass  # Pillow no instalado
    except Exception as e:
        print(f"  [Pillow error]: {e}")
    return None


# ──────────────────────────────────────────────
# 5. mtime / ctime (último recurso)
# ──────────────────────────────────────────────
def _from_filesystem(filepath):
    """Usa la fecha de modificación del archivo."""
    import os

    try:
        stat = os.stat(filepath)
        # Usar el menor entre mtime y ctime (más probable que sea original)
        ts = min(stat.st_mtime, stat.st_ctime)
        dt = datetime.fromtimestamp(ts)
        return (dt.year, dt.month, dt.day)
    except Exception:
        return None


# ──────────────────────────────────────────────
# ORQUESTADOR PRINCIPAL
# ──────────────────────────────────────────────
def get_photo_date(filepath):
    """
    Intenta obtener la fecha original de una foto
    usando múltiples estrategias en orden de confiabilidad.
    """
    strategies = [
        ("exiftool", _from_metadata),
        ("binary", _from_jpeg_binary),
        ("pillow", _from_pillow),
        ("filename", _from_filename),
        ("filesystem", _from_filesystem),
    ]

    print(f"\nBuscando fecha para: {Path(filepath).name}")
    for name, func in strategies:
        result = func(filepath)
        if result and _is_reasonable_date(result):
            print(f"  ✓ Encontrada via [{name}]: {result}")
            # Asegurar que siempre devolvemos (y, m, d, source)
            return (*result, name)
        else:
            print(f"  ✗ Nada en [{name}]")

    print(f"  ✗✗ Sin fecha válida encontrada")
    return None


def format_date(year, month, day):
    """Returns (day_str, month_name) or (None, None)."""
    try:
        dt = datetime(year, month, day)
        return f"{dt.day:02d}-{DAYS[dt.weekday()]}", MONTHS[month - 1]
    except:
        return None, None
