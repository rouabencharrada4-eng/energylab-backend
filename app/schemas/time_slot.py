from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime
from app.schemas.service import ServiceOut
from app.schemas.coach import CoachOut

class TimeSlotBase(BaseModel):
    service_id: str
    coach_id:   Optional[str] = None
    date:       date
    start_time: time
    end_time:   time
    capacity:   Optional[int] = None
    is_active:  bool          = True

class TimeSlotCreate(TimeSlotBase):
    pass

class TimeSlotUpdate(BaseModel):
    date:       Optional[date] = None
    start_time: Optional[time] = None
    end_time:   Optional[time] = None
    capacity:   Optional[int]  = None
    is_active:  Optional[bool] = None

class TimeSlotOut(TimeSlotBase):
    id:         str
    created_at: datetime
    service:    Optional[ServiceOut] = None
    coach:      Optional[CoachOut]   = None

    class Config:
        from_attributes = True