# app/crud/site_content.py
from sqlalchemy.orm import Session
from app.db.models import SiteContent


def get_all(db: Session) -> dict:
    rows = db.query(SiteContent).all()
    return {row.key: row.value for row in rows}


def bulk_upsert(db: Session, values: dict) -> dict:
    # Ignore blank/None values — the admin form sends every key on every
    # save, and an empty field almost always means "never set", not
    # "clear this out".
    values = {k: v for k, v in values.items() if v not in (None, "")}

    existing = {row.key: row for row in db.query(SiteContent).filter(SiteContent.key.in_(values.keys())).all()}
    for key, value in values.items():
        if key in existing:
            existing[key].value = value
        else:
            db.add(SiteContent(key=key, value=value))
    db.commit()
    return get_all(db)


def delete_key(db: Session, key: str) -> None:
    """Remove a key entirely so the public GET omits it and the
    frontend's hardcoded default takes back over."""
    row = db.query(SiteContent).filter(SiteContent.key == key).first()
    if row:
        db.delete(row)
        db.commit()