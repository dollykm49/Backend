import json
from pathlib import Path
from typing import Dict, Tuple

BASE_DIR = Path(__file__).resolve().parents[2]
STORAGE_ROOT = BASE_DIR / "storage"
USERS_ROOT = STORAGE_ROOT / "users"
TEMP_UPLOADS_ROOT = STORAGE_ROOT / "temp_uploads"


def create_comic_directories(user_id: str, comic_id: str) -> Dict[str, Path]:
    """Create the full directory tree for a given user's comic."""
    base = USERS_ROOT / user_id / "comics" / comic_id
    original = base / "original"
    processed = base / "processed"
    analysis = base / "analysis"
    reports = base / "reports"

    for path in [original, processed, analysis, reports]:
        path.mkdir(parents=True, exist_ok=True)

    return {
        "base": base,
        "original": original,
        "processed": processed,
        "analysis": analysis,
        "reports": reports,
    }


async def save_original_uploads(front_file, back_file, original_dir: Path) -> Dict[str, Path]:
    """Save uploaded front/back images to the original/ folder."""
    front_bytes = await front_file.read()
    back_bytes = await back_file.read()

    front_path = original_dir / "front_" + front_file.filename
    back_path = original_dir / "back_" + back_file.filename

    front_path.write_bytes(front_bytes)
    back_path.write_bytes(back_bytes)

    return {"front": front_path, "back": back_path}


def save_analysis(subgrades: dict, analysis_dir: Path) -> Path:
    """Persist subgrades/analysis JSON to disk."""
    analysis_path = analysis_dir / "subgrades.json"
    analysis_path.write_text(json.dumps(subgrades, indent=2), encoding="utf-8")
    return analysis_path
