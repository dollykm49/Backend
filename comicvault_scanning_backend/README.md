# ComicVault Scanning Backend

This is a minimal FastAPI backend that implements the scanning/grading/storage
pipeline we discussed:

- `POST /api/comics/grade`
  - form-data: `user_id`, `front` (file), `back` (file)
  - creates folder structure under `storage/users/<user_id>/comics/<comic_id>/`
  - saves original uploads
  - runs basic preprocessing
  - computes placeholder subgrades
  - writes `analysis/subgrades.json`
  - generates `reports/grading_report.pdf`

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Then hit:

- `GET http://localhost:8000/health`
- `POST http://localhost:8000/api/comics/grade`
  with `form-data`:
    - `user_id`: e.g. `test-user`
    - `front`: front cover image file
    - `back`: back cover image file

All generated data will be stored in the `storage/` directory.
```

You can later swap out `app/services/grading.py` with a real ML model,
or extend `reports.py` for fancier multi-page reports.
