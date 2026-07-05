from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum
from app.schemas.time_slot import TimeSlotOut
from app.schemas.user import UserOut

class BookingStatusEnum(str, Enum):
    pending   = "pending"
    accepted  = "accepted"
    rejected  = "rejected"
    cancelled = "cancelled"

class BookingCreate(BaseModel):
    time_slot_id:   str
    customer_phone: str
    customer_notes: Optional[str] = None

class BookingStatusUpdate(BaseModel):
    status:      BookingStatusEnum
    admin_notes: Optional[str] = None

class BookingOut(BaseModel):
    id:             str
    customer_id:    str
    time_slot_id:   str
    status:         BookingStatusEnum
    customer_phone: Optional[str]    = None
    customer_notes: Optional[str]    = None
    admin_notes:    Optional[str]    = None
    created_at:     datetime
    updated_at:     datetime
    time_slot:      Optional[TimeSlotOut] = None
    customer:       Optional[UserOut]     = None

    class Config:
        from_attributes = True