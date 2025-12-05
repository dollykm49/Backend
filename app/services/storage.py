import json
from pathlib import Path
from typing import Dict

BASE_DIR = Path(__file__).resolve().parents[2]
STORAGE_ROOT = BASE_DIR / "storage"
USERS_ROOT = STORAGE_ROOT / "users"
TEMP_UPLOADS_ROOT = STORAGE_ROOT / "temp_uploads"


def create_comic_directories(user_id: str, comic_id: str) -> Dict[str, Path]:
    """Create the full directory tree for a user's comic (Platinum version)."""

    base = USERS_ROOT / user_id / "comics" / comic_id
    original = base / "original"
    analysis = base / "analysis"
    reports = base / "reports"

    for path in [original, analysis, reports]:
        path.mkdir(parents=True, exist_ok=True)

    return {
        "base": base,
        "original": original,
        "analysis": analysis,
        "reports": reports,
    }


async def save_original_uploads(front_file, back_file, original_dir: Path) -> Dict[str, Path]:
    """Save uploaded front/back images into original/."""

    # Safety: filenames can be None depending on frontend
    front_name = front_file.filename or "front.jpg"
    back_name = back_file.filename or "back.jpg"

    front_bytes = await front_file.read()
    back_bytes = await back_file.read()

    front_path = original_dir / f"front_{front_name}"
    back_path = original_dir / f"back_{back_name}"

    front_path.write_bytes(front_bytes)
    back_path.write_bytes(back_bytes)

    return {"front": front_path, "back": back_path}


def save_analysis(grading_result: dict, analysis_dir: Path) -> Path:
    """
    Save the COMPLETE grading_result JSON (not just subgrades).
    This includes:
    - subgrades
    - final grade
    - notes
    - confidence
    - flags (restoration, pressing benefit, page color)
    """

    analysis_path = analysis_dir / "grading_result.json"
    analysis_path.write_text(json.dumps(grading_result, indent=2), encoding="utf-8")
    return analysis_path
