from sqlalchemy.orm import Session
from app.db.models import Service
from app.schemas.service import ServiceCreate, ServiceUpdate

def get_all(db: Session):
    return db.query(Service).order_by(Service.name).all()

def get_by_id(db: Session, service_id: str):
    return db.query(Service).filter(Service.id == service_id).first()

def create(db: Session, data: ServiceCreate):
    service = Service(**data.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    return service

def update(db: Session, service: Service, data: ServiceUpdate):
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(service, field, value)
    db.commit()
    db.refresh(service)
    return service

def delete(db: Session, service: Service):
    db.delete(service)
    db.commit()