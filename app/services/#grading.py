from pathlib import Path
from typing import Dict

import numpy as np
from PIL import Image, ImageFilter


def _image_score(path: Path) -> float:
    """Very simple heuristic scoring function.

    This is a placeholder so the pipeline runs end-to-end.
    You can replace this with a proper ML model later.

    It looks at:
    - edge strength (sharper = better)
    - brightness distribution
    and maps that to a 0.0–10.0 scale.
    """
    img = Image.open(path).convert("L")  # grayscale
    arr = np.array(img, dtype=float)

    # Edge strength via Laplacian-like filter
    edges = img.filter(ImageFilter.FIND_EDGES)
    edges_arr = np.array(edges, dtype=float)
    edge_strength = edges_arr.mean() / 255.0  # 0–1

    # Brightness score: avoid too dark / too blown out
    mean_brightness = arr.mean() / 255.0  # 0–1
    brightness_score = 1.0 - abs(mean_brightness - 0.5) * 2  # peak at 0.5

    raw_score = (0.6 * edge_strength + 0.4 * brightness_score)
    score_0_10 = max(0.0, min(10.0, raw_score * 10.0))
    return round(score_0_10, 1)


def grade_comic(processed_paths: Dict[str, Path]) -> Dict[str, float]:
    """Compute subgrades and a final grade from processed images.

    For now, we derive subgrades from simple stats of the front/back images.
    This is intentionally transparent and easy to swap out later.
    """
    front_score = _image_score(processed_paths["front"])
    back_score = _image_score(processed_paths["back"])

    # Derive fake-but-consistent subgrades from the two views
    corners = round((front_score * 0.6 + back_score * 0.4), 1)
    spine = round((front_score * 0.7 + back_score * 0.3), 1)
    surface = round((front_score * 0.5 + back_score * 0.5), 1)
    centering = round(min(10.0, front_score + 0.3), 1)
    color = round(min(10.0, (front_score * 0.8 + back_score * 0.2)), 1)

    subgrades = {
        "corners": corners,
        "spine": spine,
        "surface": surface,
        "centering": centering,
        "color": color,
    }

    # Simple weighted average for final grade
    weights = {
        "corners": 0.2,
        "spine": 0.25,
        "surface": 0.25,
        "centering": 0.15,
        "color": 0.15,
    }

    final_grade = 0.0
    for key, weight in weights.items():
        final_grade += subgrades[key] * weight

    subgrades["final"] = round(final_grade, 1)
    return subgrades
