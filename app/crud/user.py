from sqlalchemy.orm import Session
from app.db.models import User
from app.schemas.user import UserCreate, UserUpdate

def get_by_clerk_id(db: Session, clerk_id: str):
    return db.query(User).filter(User.clerk_id == clerk_id).first()

def get_by_id(db: Session, user_id: str):
    return db.query(User).filter(User.id == user_id).first()

def get_all(db: Session):
    return db.query(User).order_by(User.created_at.desc()).all()

def create(db: Session, data: UserCreate):
    user = User(**data.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update(db: Session, user: User, data: UserUpdate):
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user

def delete(db: Session, user: User):
    db.delete(user)
    db.commit()