"""Image upload validation: type, size and dimensions."""
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException, UploadFile
from PIL import Image

from app.core.config import get_settings

settings = get_settings()


class ImageValidationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)


def validate_image(file: UploadFile) -> bytes:
    ext = Path(file.filename or "").suffix.lower() if file.filename else ""
    if ext and ext not in settings.allowed_extensions:
        raise ImageValidationError(
            f"Invalid file type '{ext}'. Allowed: {', '.join(sorted(settings.allowed_extensions))}."
        )

    content = file.file.read()
    max_bytes = int(settings.MAX_UPLOAD_MB * 1024 * 1024)
    if len(content) > max_bytes:
        raise ImageValidationError(
            f"File too large ({len(content) / 1024 / 1024:.1f} MB). Maximum is {settings.MAX_UPLOAD_MB:.0f} MB."
        )

    try:
        with Image.open(BytesIO(content)) as img:
            img.verify()
    except Exception as exc:  # noqa: BLE001
        raise ImageValidationError("Invalid or corrupted image file.") from exc

    try:
        with Image.open(BytesIO(content)) as img:
            width, height = img.size
            if width < 64 or height < 64:
                raise ImageValidationError("Image dimensions too small (min 64x64 px).")
    except ImageValidationError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise ImageValidationError("Could not read image dimensions.") from exc

    return content
