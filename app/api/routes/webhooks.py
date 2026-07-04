from fastapi import APIRouter, Request, HTTPException, Header
from svix.webhooks import Webhook, WebhookVerificationError
from app.db.database import SessionLocal
from app.schemas.user import UserCreate
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
            existing  = user_crud.get_by_clerk_id(db, clerk_id)
            if not existing:
                user_crud.create(db, UserCreate(
                    clerk_id=clerk_id,
                    email=email,
                    full_name=full_name,
                ))
        finally:
            db.close()

    return {"status": "ok"}