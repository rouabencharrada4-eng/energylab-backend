# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.db.database import Base, engine
from app.api.routes import (
    webhooks, users, coaches, services, time_slots, bookings, announcements,
    site_content, gallery, showcase, events,
)
import os
import traceback
import logging

log = logging.getLogger("uvicorn.error")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="EnergyLab API", version="1.0.0")

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]
# FRONTEND_URL can be a single URL or comma-separated list
for url in settings.FRONTEND_URL.split(","):
    url = url.strip()
    if url and url not in ALLOWED_ORIGINS:
        ALLOWED_ORIGINS.append(url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    log.error(f"Unhandled error on {request.method} {request.url.path}:\n{tb}")
    response = JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error",
            "error": str(exc),
            "traceback": tb.splitlines(),  # TEMPORARY — remove before real production use
        },
    )
    # A registered handler for the bare Exception class runs in Starlette's
    # ServerErrorMiddleware, which sits OUTSIDE CORSMiddleware — so without this,
    # every unhandled 500 arrives at the browser with no CORS header and gets
    # reported as a CORS error instead of showing the real failure.
    origin = request.headers.get("origin")
    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

for _dir in ("services", "gallery", "showcase", "site-content", "events"):
    os.makedirs(f"uploads/{_dir}", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(webhooks.router,      prefix="")
app.include_router(users.router,         prefix="")
app.include_router(coaches.router,       prefix="")
app.include_router(services.router,      prefix="")
app.include_router(time_slots.router,    prefix="")
app.include_router(bookings.router,      prefix="")
app.include_router(announcements.router, prefix="")
app.include_router(site_content.router,  prefix="")
app.include_router(gallery.router,       prefix="")
app.include_router(showcase.router,      prefix="")
app.include_router(events.router,        prefix="")

@app.get("/health")
def health():
    return {"status": "ok"}