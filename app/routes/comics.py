from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import uuid

from app.services import storage, openai_hybrid_grading, reports

router = APIRouter()


@router.post("/grade")
async def grade_comic(
    user_id: str = Form(...),
    front: UploadFile = File(...),
    back: UploadFile = File(...),
):
    if not front.filename or not back.filename:
        raise HTTPException(status_code=400, detail="Both front and back images are required.")

    comic_id = str(uuid.uuid4())

    # 1) Create directory structure
    dirs = storage.create_comic_directories(user_id, comic_id)

    # 2) Save originals
    original_paths = await storage.save_original_uploads(front, back, dirs["original"])

    # 3) Hybrid AI + algorithm grading
    try:
        grading_result = openai_hybrid_grading.grade_comic(
            front_path=original_paths["front"],
            back_path=original_paths["back"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI grading failed: {e}")

    # grading_result shape:
    # {
    #   "subgrades": { ... },
    #   "final": number,
    #   "notes": "text",
    #   "confidence": number (0-1),
    #   "flags": {...}
    # }

    # 4) Save analysis JSON
    analysis_path = storage.save_analysis(grading_result, dirs["analysis"])

    # 5) Generate PDF report
    report_path = reports.generate_report(
        user_id=user_id,
        comic_id=comic_id,
        grading_result=grading_result,
        report_dir=dirs["reports"],
    )

    return {
        "user_id": user_id,
        "comic_id": comic_id,
        "subgrades": grading_result["subgrades"],
        "final": grading_result["final"],
        "notes": grading_result["notes"],
        "confidence": grading_result["confidence"],
        "flags": grading_result.get("flags", {}),
        "analysis_path": str(analysis_path),
        "report_path": str(report_path),
    }
