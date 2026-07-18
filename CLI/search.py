"""File discovery with video extensions and sidecar-aware scanning."""
import os

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".heic", ".raw", ".dng",
}

VIDEO_EXTENSIONS = {
    ".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm", ".m4v", ".3gp",
}

ALL_MEDIA = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS


def find_images(source_dir, exclude_dir=None):
    """Yield image filepaths found recursively in source_dir."""
    for root, dirs, files in os.walk(source_dir):
        if exclude_dir:
            dirs[:] = [
                d for d in dirs
                if os.path.realpath(os.path.join(root, d)) != exclude_dir
            ]
        for filename in files:
            if os.path.splitext(filename)[1].lower() in IMAGE_EXTENSIONS:
                yield os.path.join(root, filename)


def find_all_media(source_dir, exclude_dir=None):
    """Yield all media (image + video) filepaths."""
    for root, dirs, files in os.walk(source_dir):
        if exclude_dir:
            dirs[:] = [
                d for d in dirs
                if os.path.realpath(os.path.join(root, d)) != exclude_dir
            ]
        for filename in files:
            if os.path.splitext(filename)[1].lower() in ALL_MEDIA:
                yield os.path.join(root, filename)


def has_sidecar(media_path):
    """Check if a media file has a Google Takeout sidecar JSON."""
    return os.path.isfile(f"{media_path}.json")


def find_media_with_sidecars(source_dir, exclude_dir=None):
    """Yield (filepath, has_sidecar) tuples for all media files."""
    for filepath in find_all_media(source_dir, exclude_dir):
        yield filepath, has_sidecar(filepath)
