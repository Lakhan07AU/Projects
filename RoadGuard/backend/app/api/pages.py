"""Public web endpoints (HTML pages) and static file serving."""
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.core.config import get_settings

settings = get_settings()
router = APIRouter(include_in_schema=False)

FRONTEND = Path(__file__).resolve().parent.parent.parent.parent / "frontend"

_PAGES = {
    "": "index.html",
    "/login": "login.html",
    "/register": "register.html",
    "/report": "report.html",
    "/complaints": "complaints.html",
    "/complaint-details": "complaint-details.html",
    "/map": "map.html",
    "/profile": "profile.html",
    "/notifications": "notifications.html",
    "/government": "government/dashboard.html",
    "/government/dashboard": "government/dashboard.html",
    "/government/potholes": "government/potholes.html",
    "/government/pothole-details": "government/pothole-details.html",
    "/government/repairs": "government/repairs.html",
    "/government/analytics": "government/analytics.html",
    "/government/users": "government/users.html",
    "/government/cost-rates": "government/cost-rates.html",
    "/repair-team": "repair-team/dashboard.html",
    "/repair-team/dashboard": "repair-team/dashboard.html",
    "/repair-team/assignments": "repair-team/assignments.html",
    "/repair-team/repair-details": "repair-team/repair-details.html",
}


def _serve_uploads(path: str):
    """Serve uploaded images so /uploads/... URLs always resolve."""
    if path.startswith("uploads/"):
        candidate = (settings.storage_path / path[len("uploads/"):]).resolve()
        if candidate.is_relative_to(settings.storage_path.resolve()) and candidate.is_file():
            return FileResponse(candidate)
    return None


def _serve_frontend_file(path: str):
    """Serve a real static file (css/js/images/html) from the frontend dir."""
    if not path or path.startswith("api/") or path.startswith("uploads/"):
        return None
    candidate = (FRONTEND / path).resolve()
    if candidate.is_relative_to(FRONTEND.resolve()) and candidate.is_file():
        return FileResponse(candidate)
    return None


@router.get("/{path:path}")
def serve_page(path: str):
    # 1. Real files under uploads (via storage path).
    resp = _serve_uploads(path)
    if resp:
        return resp
    # 2. Real static files in the frontend directory (css, js, html, images).
    resp = _serve_frontend_file(path)
    if resp:
        return resp
    # 3. Clean-URL page map (SPA-style routes).
    page = _PAGES.get(f"/{path}")
    if page and (FRONTEND / page).exists():
        return FileResponse(FRONTEND / page)
    # 4. SPA fallback.
    return FileResponse(FRONTEND / "index.html")
