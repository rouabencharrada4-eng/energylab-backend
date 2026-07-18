from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

class RoleEnum(str, Enum):
    admin    = "admin"
    customer = "customer"

class UserBase(BaseModel):
    email:     EmailStr
    full_name: str
    phone:     Optional[str] = None
    address:   Optional[str] = None

class UserCreate(UserBase):
    clerk_id: str
    role:     RoleEnum = RoleEnum.customer

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone:     Optional[str] = None
    address:   Optional[str] = None

class UserOut(UserBase):
    id:         str
    clerk_id:   str
    role:       RoleEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True