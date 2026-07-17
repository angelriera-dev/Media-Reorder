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


def find_images(source_dir):
    """Yields image filepaths found recursively in source_dir."""
    for root, _, files in os.walk(source_dir):
        for filename in files:
            if os.path.splitext(filename)[1].lower() in IMAGE_EXTENSIONS:
                yield os.path.join(root, filename)
