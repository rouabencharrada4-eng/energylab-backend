from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.db.database import Base, engine
from app.api.routes import webhooks, users, coaches, services, time_slots, bookings, announcements
import os
import traceback
import logging

log = logging.getLogger("uvicorn.error")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="EnergyLab API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        settings.FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    log.error(f"Unhandled error on {request.method} {request.url.path}:\n{tb}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error",
            "error": str(exc),
            "traceback": tb.splitlines(),  # TEMPORARY — remove before real production use
        },
    )

os.makedirs("uploads/services", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

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