from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Dict
import uuid

from app.services import storage, preprocessing, grading, reports

router = APIRouter()


@router.post("/grade")
async def grade_comic(
    user_id: str = Form(...),
    front: UploadFile = File(...),
    back: UploadFile = File(...),
) -> Dict:
    """Upload front/back images, run grading pipeline, and return results.

    This endpoint:
    - creates the folder structure for this comic
    - stores originals
    - runs preprocessing
    - computes subgrades + final grade
    - saves analysis JSON
    - generates a PDF report
    """
    if not front.filename or not back.filename:
        raise HTTPException(status_code=400, detail="Both front and back images are required.")

    comic_id = str(uuid.uuid4())

    # Prepare directory structure
    dirs = storage.create_comic_directories(user_id, comic_id)

    # Save originals
    original_paths = await storage.save_original_uploads(front, back, dirs["original"])

    # Preprocess images
    processed_paths = preprocessing.process_images(original_paths, dirs["processed"])

    # Compute grades
    subgrades = grading.grade_comic(processed_paths)

    # Save analysis JSON
    analysis_path = storage.save_analysis(subgrades, dirs["analysis"])

    # Generate PDF report
    report_path = reports.generate_report(user_id, comic_id, subgrades, dirs["reports"])

    return {
        "user_id": user_id,
        "comic_id": comic_id,
        "subgrades": subgrades,
        "analysis_path": str(analysis_path),
        "report_path": str(report_path),
    }
