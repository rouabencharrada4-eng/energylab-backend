from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CoachBase(BaseModel):
    full_name: str
    bio:       Optional[str] = None
    is_active: bool = True

class CoachCreate(CoachBase):
    service_ids: list[str] = []

class CoachUpdate(BaseModel):
    full_name:   Optional[str]       = None
    bio:         Optional[str]       = None
    is_active:   Optional[bool]      = None
    service_ids: Optional[list[str]] = None

class CoachOut(CoachBase):
    id:         str
    created_at: datetime

    class Config:
        from_attributes = True