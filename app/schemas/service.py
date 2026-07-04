from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ServiceBase(BaseModel):
    name:             str
    description:      Optional[str] = None
    duration_minutes: int           = 60
    max_capacity:     int           = 1
    requires_coach:   bool          = True
    is_active:        bool          = True

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name:             Optional[str]  = None
    description:      Optional[str]  = None
    duration_minutes: Optional[int]  = None
    max_capacity:     Optional[int]  = None
    requires_coach:   Optional[bool] = None
    is_active:        Optional[bool] = None

class ServiceOut(ServiceBase):
    id:         str
    created_at: datetime

    class Config:
        from_attributes = True