# app/db/models.py
import uuid
from sqlalchemy import (
    Column, String, Boolean, Integer, Text, Date, Time,
    ForeignKey, Enum, DateTime, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.db.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class RoleEnum(str, enum.Enum):
    admin    = "admin"
    customer = "customer"


class BookingStatusEnum(str, enum.Enum):
    pending   = "pending"
    accepted  = "accepted"
    rejected  = "rejected"
    cancelled = "cancelled"


class User(Base):
    __tablename__ = "users"

    id         = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    clerk_id   = Column(String, unique=True, nullable=False, index=True)
    email      = Column(String, unique=True, nullable=False)
    full_name  = Column(String, nullable=False)
    phone      = Column(String, nullable=True)
    address    = Column(String, nullable=True)
    role       = Column(Enum(RoleEnum), default=RoleEnum.customer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    bookings   = relationship("Booking", back_populates="customer", cascade="all, delete-orphan")


class Coach(Base):
    __tablename__ = "coaches"

    id         = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    full_name  = Column(String, nullable=False)
    bio        = Column(Text, nullable=True)
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    services   = relationship("CoachService", back_populates="coach", cascade="all, delete-orphan")
    time_slots = relationship("TimeSlot", back_populates="coach")


class Service(Base):
    __tablename__ = "services"

    id               = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name             = Column(String, nullable=False)
    description      = Column(Text, nullable=True)
    duration_minutes = Column(Integer, nullable=False, default=60)
    max_capacity     = Column(Integer, nullable=False, default=1)
    requires_coach   = Column(Boolean, default=True)
    is_active        = Column(Boolean, default=True)
    created_at       = Column(DateTime, server_default=func.now())
    image_url = Column(String, nullable=True)

    coaches    = relationship("CoachService", back_populates="service", cascade="all, delete-orphan")
    time_slots = relationship("TimeSlot", back_populates="service")


class CoachService(Base):
    __tablename__ = "coach_services"

    coach_id   = Column(UUID(as_uuid=False), ForeignKey("coaches.id"), primary_key=True)
    service_id = Column(UUID(as_uuid=False), ForeignKey("services.id"), primary_key=True)

    coach   = relationship("Coach",   back_populates="services")
    service = relationship("Service", back_populates="coaches")


class TimeSlot(Base):
    __tablename__ = "time_slots"

    id         = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    service_id = Column(UUID(as_uuid=False), ForeignKey("services.id"), nullable=False)
    coach_id   = Column(UUID(as_uuid=False), ForeignKey("coaches.id"),  nullable=True)
    date       = Column(Date,  nullable=False)
    start_time = Column(Time,  nullable=False)
    end_time   = Column(Time,  nullable=False)
    capacity   = Column(Integer, nullable=True)
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    service  = relationship("Service", back_populates="time_slots")
    coach    = relationship("Coach",   back_populates="time_slots")
    bookings = relationship("Booking", back_populates="time_slot")


class Booking(Base):
    __tablename__ = "bookings"

    id             = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    customer_id    = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    time_slot_id   = Column(UUID(as_uuid=False), ForeignKey("time_slots.id"), nullable=False)
    status         = Column(Enum(BookingStatusEnum), default=BookingStatusEnum.pending, nullable=False)
    customer_phone = Column(String, nullable=True)
    customer_notes = Column(Text, nullable=True)
    admin_notes    = Column(Text, nullable=True)
    created_at     = Column(DateTime, server_default=func.now())
    updated_at     = Column(DateTime, server_default=func.now(), onupdate=func.now())

    customer  = relationship("User",     back_populates="bookings")
    time_slot = relationship("TimeSlot", back_populates="bookings")


class Announcement(Base):
    __tablename__ = "announcements"

    id         = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    content    = Column(Text, nullable=False)
    is_active  = Column(Boolean, default=True)
    starts_at  = Column(DateTime, nullable=True)
    ends_at    = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class SiteContent(Base):
    """
    Free-form key/value store for editable site copy & images
    (hero title, about paragraphs, contact info, logo, etc).
    Lets the admin edit site text/images without a code deploy,
    and lets us add new editable fields later without a migration.
    """
    __tablename__ = "site_content"

    key        = Column(String, primary_key=True)
    value      = Column(Text, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class GalleryImage(Base):
    __tablename__ = "gallery_images"

    id         = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    image_url  = Column(String, nullable=False)
    caption    = Column(String, nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class ShowcaseItem(Base):
    """The 'What We Offer' cards on the homepage — editable from the admin dashboard."""
    __tablename__ = "showcase_items"

    id          = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name        = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    image_url   = Column(String, nullable=True)
    align       = Column(String, default="left")   # "left" | "right"
    bookable    = Column(Boolean, default=False)    # show a "Book Now" button
    sort_order  = Column(Integer, default=0, nullable=False)
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime, server_default=func.now())