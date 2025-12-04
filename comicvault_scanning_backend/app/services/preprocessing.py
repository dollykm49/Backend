from pathlib import Path
from typing import Dict

from PIL import Image, ImageOps, ImageEnhance


def _normalize_image(path: Path) -> Path:
    """Basic preprocessing to make grading more consistent.

    - convert to RGB
    - auto-orient
    - resize to reasonable max size
    - slight contrast enhancement
    """
    img = Image.open(path)

    # Ensure RGB
    img = img.convert("RGB")

    # Auto-orient based on EXIF
    img = ImageOps.exif_transpose(img)

    # Resize if huge
    max_dim = 2000
    w, h = img.size
    scale = min(max_dim / max(w, h), 1.0)
    if scale < 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    # Gentle contrast boost
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.05)

    # Save back to a new processed file
    processed_path = path.parent.parent / "processed" / path.name
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(processed_path, format="JPEG", quality=90)

    return processed_path


def process_images(original_paths: Dict[str, Path], processed_dir: Path) -> Dict[str, Path]:
    """Run preprocessing on front/back originals and return processed paths."""
    processed = {}
    for key, path in original_paths.items():
        processed[key] = _normalize_image(path)
    return processed
