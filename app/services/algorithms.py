import numpy as np


def normalize_scores(raw_scores: dict) -> dict:
    """
    Apply consistent grading adjustments to AI raw scores.
    Returns dict with normalized subgrades + 'final'.
    """

    scores = raw_scores.copy()

    # 1. Clamp everything to [0.5, 10.0]
    for key in scores:
        scores[key] = float(np.clip(scores[key], 0.5, 10.0))

    # 2. Weight spine and corners a bit more, centering slightly less
    weights_boost = {
        "corners": 1.05,
        "spine": 1.15,
        "surface": 1.00,
        "centering": 0.95,
        "color": 1.00,
    }

    for key, factor in weights_boost.items():
        scores[key] = float(np.clip(scores[key] * factor, 0.5, 10.0))

    # 3. Weighted final grade (similar to pro services)
    final = np.average(
        [
            scores["corners"],
            scores["spine"],
            scores["surface"],
            scores["centering"],
            scores["color"],
        ],
        weights=[2, 3, 2, 1, 2],
    )

    scores["final"] = float(round(final, 1))
    return scores


def compute_confidence(opinion_a: dict, opinion_b: dict) -> float:
    """
    Simple confidence metric based on how close the two AI opinions are.
    Lower disagreement = higher confidence.
    """

    keys = ["corners", "spine", "surface", "centering", "color"]
    diffs = []
    for k in keys:
        a = float(opinion_a.get(k, 0))
        b = float(opinion_b.get(k, 0))
        diffs.append(abs(a - b))

    avg_diff = np.mean(diffs) if diffs else 0.0

    # 0 diff -> 0.98, 2.0 diff -> ~0.5, >3 diff -> low
    confidence = float(np.clip(1.0 - (avg_diff / 3.0), 0.3, 0.98))
    return round(confidence, 2)
