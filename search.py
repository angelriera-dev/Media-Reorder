import os

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".webp",
    ".heic",
    ".raw",
    ".dng",
}


def find_images(source_dir, exclude_dir=None):
    """Yields image filepaths found recursively in source_dir.
    
    Args:
        source_dir: Root directory to scan.
        exclude_dir: Absolute real path to exclude (e.g. output_dir).
    """
    for root, dirs, files in os.walk(source_dir):
        # Prune output_dir from traversal to avoid scanning already-copied files
        if exclude_dir:
            dirs[:] = [
                d for d in dirs
                if os.path.realpath(os.path.join(root, d)) != exclude_dir
            ]
        for filename in files:
            if os.path.splitext(filename)[1].lower() in IMAGE_EXTENSIONS:
                yield os.path.join(root, filename)
