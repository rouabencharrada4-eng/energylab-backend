from fastapi import APIRouter, Request, HTTPException, Header
from svix.webhooks import Webhook, WebhookVerificationError
from app.db.database import SessionLocal
from app.schemas.user import UserCreate, UserUpdate
from app.crud import user as user_crud
from app.core.config import settings

router = APIRouter()

@router.post("/webhooks/clerk")
async def clerk_webhook(
    request: Request,
    svix_id:        str = Header(None, alias="svix-id"),
    svix_timestamp: str = Header(None, alias="svix-timestamp"),
    svix_signature: str = Header(None, alias="svix-signature"),
):
    payload = await request.body()
    headers = {
        "svix-id":        svix_id,
        "svix-timestamp": svix_timestamp,
        "svix-signature": svix_signature,
    }

    try:
        wh = Webhook(settings.CLERK_WEBHOOK_SECRET)
        event = wh.verify(payload, headers)
    except WebhookVerificationError:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    event_type = event.get("type")
    data       = event.get("data", {})

    if event_type == "user.created":
        db = SessionLocal()
        try:
            clerk_id  = data["id"]
            email     = data["email_addresses"][0]["email_address"]
            full_name = f"{data.get('first_name', '')} {data.get('last_name', '')}".strip() or email
            # phone/address aren't native Clerk fields for unverified, custom
            # data like this -- they're collected via the sign-up form and
            # ride along in unsafe_metadata instead.
            metadata  = data.get("unsafe_metadata", {}) or {}
            phone     = metadata.get("phone") or None
            address   = metadata.get("address") or None
            existing  = user_crud.get_by_clerk_id(db, clerk_id)
            if not existing:
                user_crud.create(db, UserCreate(
                    clerk_id=clerk_id,
                    email=email,
                    full_name=full_name,
                    phone=phone,
                    address=address,
                ))
        finally:
            db.close()

    elif event_type == "user.updated":
        db = SessionLocal()
        try:
            clerk_id = data["id"]
            existing = user_crud.get_by_clerk_id(db, clerk_id)
            if existing:
                full_name = f"{data.get('first_name', '')} {data.get('last_name', '')}".strip() or existing.full_name
                metadata  = data.get("unsafe_metadata", {}) or {}
                user_crud.update(db, existing, UserUpdate(
                    full_name=full_name,
                    phone=metadata.get("phone") or existing.phone,
                    address=metadata.get("address") or existing.address,
                ))
        finally:
            db.close()

    return {"status": "ok"}