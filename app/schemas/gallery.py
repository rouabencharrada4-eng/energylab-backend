# app/schemas/gallery.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class GalleryImageCreate(BaseModel):
    caption: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True


class GalleryImageUpdate(BaseModel):
    caption: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class GalleryImageOut(BaseModel):
    id: str
    image_url: str
    caption: Optional[str] = None
    sort_order: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True