# app/crud/site_content.py
from sqlalchemy.orm import Session
from app.db.models import SiteContent


def get_all(db: Session) -> dict:
    rows = db.query(SiteContent).all()
    return {row.key: row.value for row in rows}


def bulk_upsert(db: Session, values: dict) -> dict:
    existing = {row.key: row for row in db.query(SiteContent).filter(SiteContent.key.in_(values.keys())).all()}
    for key, value in values.items():
        if key in existing:
            existing[key].value = value
        else:
            db.add(SiteContent(key=key, value=value))
    db.commit()
    return get_all(db)