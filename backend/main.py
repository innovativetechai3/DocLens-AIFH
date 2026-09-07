from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.routes.documents import router as documents_router
from backend.routes.query import router as query_router


app = FastAPI(
    title="DocLens AI",
    description="Evidence Grounded Document Intelligence System"
)

# Project paths

BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"

# API routes

app.include_router(
    documents_router
)

app.include_router(
    query_router
)

# Static Frontend
# Serve frontend assets such as CSS, JavaScript, and images.
app.mount(
    "/static",
    StaticFiles(
        directory=str(FRONTEND_DIR)
    ),
    name="static"
)


@app.get("/")
def serve_frontend():
    """Serve the DocLens AI web interface."""
    return FileResponse(
        FRONTEND_DIR / "index.html"
    )