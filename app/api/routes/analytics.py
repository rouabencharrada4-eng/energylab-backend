from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.analytics import DashboardAnalytics
from app.crud import analytics as analytics_crud
from app.core.security import get_admin_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardAnalytics)
def get_dashboard_analytics(
    months: int = Query(6, ge=1, le=24),
    active_days: int = Query(90, ge=1, le=365),
    booking_days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    _=Depends(get_admin_user),
):
    return {
        "member_growth": analytics_crud.get_member_growth(db, months),
        "member_status": analytics_crud.get_member_status(db, active_days),
        "booking_stats": analytics_crud.get_booking_stats(db, booking_days),
        "service_distribution": analytics_crud.get_service_distribution(db),
    }