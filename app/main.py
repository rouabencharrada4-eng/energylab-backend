from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import Base, engine
from app.api.routes import webhooks, users, coaches, services, time_slots, bookings, announcements

Base.metadata.create_all(bind=engine)

app = FastAPI(title="EnergyLab API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhooks.router,      prefix="")
app.include_router(users.router,         prefix="")
app.include_router(coaches.router,       prefix="")
app.include_router(services.router,      prefix="")
app.include_router(time_slots.router,    prefix="")
app.include_router(bookings.router,      prefix="")
app.include_router(announcements.router, prefix="")

@app.get("/health")
def health():
    return {"status": "ok"}