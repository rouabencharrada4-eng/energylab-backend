from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.booking import BookingCreate, BookingStatusUpdate, BookingOut
from app.crud import booking as booking_crud
from app.core.security import get_current_user, get_admin_user

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.get("", response_model=list[BookingOut])
def get_all_bookings(db: Session=Depends(get_db), _=Depends(get_admin_user)):
    return booking_crud.get_all(db)

@router.get("/me", response_model=list[BookingOut])
def get_my_bookings(db: Session=Depends(get_db), current_user=Depends(get_current_user)):
    return booking_crud.get_by_customer(db, current_user.id)

@router.post("", response_model=BookingOut)
def create_booking(data: BookingCreate, db: Session=Depends(get_db), current_user=Depends(get_current_user)):
    return booking_crud.create(db, data, current_user.id)

@router.patch("/{booking_id}/status", response_model=BookingOut)
def update_booking_status(
    booking_id: str,
    data: BookingStatusUpdate,
    db: Session=Depends(get_db),
    current_user=Depends(get_current_user),
):
    booking = booking_crud.get_by_id(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    is_admin = current_user.role.value == "admin"
    is_owner = booking.customer_id == current_user.id

    if not is_admin and not is_owner:
        raise HTTPException(status_code=403, detail="Forbidden")

    if not is_admin and data.status.value not in ("cancelled",):
        raise HTTPException(status_code=403, detail="Customers can only cancel bookings")

    return booking_crud.update_status(db, booking, data)