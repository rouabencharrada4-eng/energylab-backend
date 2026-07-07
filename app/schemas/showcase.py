# app/schemas/showcase.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ShowcaseItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    align: str = "left"
    bookable: bool = False
    sort_order: int = 0
    is_active: bool = True


class ShowcaseItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    align: Optional[str] = None
    bookable: Optional[bool] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class ShowcaseItemOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    align: str
    bookable: bool
    sort_order: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True