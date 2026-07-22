# app/schemas/hero_image.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class HeroImageUpdate(BaseModel):
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class HeroImageOut(BaseModel):
    id: str
    image_url: str
    sort_order: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True