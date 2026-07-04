from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AnnouncementBase(BaseModel):
    content:   str
    is_active: bool              = True
    starts_at: Optional[datetime] = None
    ends_at:   Optional[datetime] = None

class AnnouncementCreate(AnnouncementBase):
    pass

class AnnouncementUpdate(BaseModel):
    content:   Optional[str]      = None
    is_active: Optional[bool]     = None
    starts_at: Optional[datetime] = None
    ends_at:   Optional[datetime] = None

class AnnouncementOut(AnnouncementBase):
    id:         str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True