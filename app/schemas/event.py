# app/schemas/event.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    event_date: Optional[datetime] = None
    is_active: bool = True


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class EventOut(EventBase):
    id: str
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True