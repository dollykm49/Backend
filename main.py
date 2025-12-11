from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import comics

app = FastAPI(
    title="ComicVault Platinum Grading Backend",
    version="1.0.0",
    description="Hybrid OpenAI + algorithmic comic grading with PDF reports."
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vaultmycomic.com",
        "https://www.vaultmycomic.com",
        "http://localhost:5173",
        "http://localhost:5177"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Provide a simple landing message so deployed instances don't return 404."""
    return {
        "message": "ComicVault Platinum Grading Backend",
        "docs": "/docs",
        "health": "/health",
        "grade_endpoint": "/api/comics/grade",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(comics.router, prefix="/api/comics", tags=["comics"])

