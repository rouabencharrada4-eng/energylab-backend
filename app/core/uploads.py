# app/core/uploads.py
#
# Single place all "admin uploads an image" endpoints go through.
#
# On Render (and most PaaS), the local filesystem is wiped on every deploy/restart —
# so images saved to disk quietly disappear. If Cloudinary credentials are set,
# we upload there instead (persistent, free tier is plenty for this use case).
# If they're not set, we fall back to local disk so local dev keeps working
# with zero setup.

import shutil
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.core.config import settings

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}

_cloudinary_configured = False
if settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY and settings.CLOUDINARY_API_SECRET:
    import cloudinary
    import cloudinary.uploader

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )
    _cloudinary_configured = True


def upload_image(file: UploadFile, folder: str) -> str:
    """
    Validates and stores an uploaded image, returning a publicly-accessible URL.
    `folder` groups uploads (e.g. "gallery", "showcase", "site-content", "services").
    """
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="File must be an image (jpeg, png, or webp)")

    if _cloudinary_configured:
        result = cloudinary.uploader.upload(
            file.file,
            folder=f"energylab/{folder}",
            resource_type="image",
        )
        return result["secure_url"]

    # --- local disk fallback (dev only — not persistent on most hosts) ---
    ext = (file.filename or "").split(".")[-1] or "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_dir = Path("uploads") / folder
    upload_dir.mkdir(parents=True, exist_ok=True)
    filepath = upload_dir / filename

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return f"{settings.BACKEND_URL}/uploads/{folder}/{filename}"


def delete_image(image_url: str) -> None:
    """Best-effort cleanup when an image is replaced/removed. Never raises."""
    try:
        if _cloudinary_configured and "res.cloudinary.com" in image_url:
            # Public ID is the path segment after /upload/v<version>/ minus the extension.
            parts = image_url.split("/upload/")
            if len(parts) == 2:
                tail = parts[1]
                tail = tail.split("/", 1)[1] if tail.startswith("v") and "/" in tail else tail
                public_id = tail.rsplit(".", 1)[0]
                cloudinary.uploader.destroy(public_id)
        elif image_url.startswith(f"{settings.BACKEND_URL}/uploads/"):
            local_path = Path(image_url.split(f"{settings.BACKEND_URL}/", 1)[1])
            local_path.unlink(missing_ok=True)
    except Exception:
        pass