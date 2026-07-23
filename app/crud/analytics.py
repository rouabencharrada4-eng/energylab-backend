from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.db.models import User, Booking, RoleEnum, Service, TimeSlot


def get_member_growth(db: Session, months: int = 6):
    cutoff = datetime.utcnow() - timedelta(days=30 * months)

    rows = (
        db.query(
            func.date_trunc("month", User.created_at).label("month"),
            func.count(User.id).label("count"),
        )
        .filter(User.role == RoleEnum.customer, User.created_at >= cutoff)
        .group_by("month")
        .order_by("month")
        .all()
    )

    total_before = (
        db.query(func.count(User.id))
        .filter(User.role == RoleEnum.customer, User.created_at < cutoff)
        .scalar()
    ) or 0

    points, running = [], total_before
    for row in rows:
        running += row.count
        points.append({
            "period": row.month.strftime("%Y-%m"),
            "new_members": row.count,
            "cumulative": running,
        })
    return points


def get_member_status(db: Session, active_days: int = 90):
    cutoff = datetime.utcnow() - timedelta(days=active_days)

    total_customers = (
        db.query(func.count(User.id)).filter(User.role == RoleEnum.customer).scalar()
    ) or 0

    active_customers = (
        db.query(func.count(func.distinct(Booking.customer_id)))
        .join(User, User.id == Booking.customer_id)
        .filter(User.role == RoleEnum.customer, Booking.created_at >= cutoff)
        .scalar()
    ) or 0

    return {
        "active": active_customers,
        "inactive": max(total_customers - active_customers, 0),
        "active_days": active_days,
    }


def get_booking_stats(db: Session, days: int = 30):
    total = db.query(func.count(Booking.id)).scalar() or 0

    status_rows = (
        db.query(Booking.status, func.count(Booking.id))
        .group_by(Booking.status)
        .all()
    )
    by_status = [{"status": s.value, "count": c} for s, c in status_rows]

    cutoff = datetime.utcnow() - timedelta(days=days)
    day_rows = (
        db.query(
            func.date(Booking.created_at).label("day"),
            func.count(Booking.id).label("count"),
        )
        .filter(Booking.created_at >= cutoff)
        .group_by("day")
        .order_by("day")
        .all()
    )
    by_day = [{"date": d.day.strftime("%Y-%m-%d"), "count": d.count} for d in day_rows]

    return {"total": total, "by_status": by_status, "by_day": by_day}


def get_service_distribution(db: Session):
    rows = (
        db.query(Service.name, func.count(Booking.id).label("count"))
        .join(TimeSlot, TimeSlot.service_id == Service.id)
        .join(Booking, Booking.time_slot_id == TimeSlot.id)
        .group_by(Service.name)
        .order_by(func.count(Booking.id).desc())
        .all()
    )
    return [{"service": name, "count": count} for name, count in rows]