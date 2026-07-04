# scripts/promote_admin.py
# Run once: python -m scripts.promote_admin someone@example.com
import sys
import httpx
from app.db.database import SessionLocal
from app.db.models import User, RoleEnum
from app.core.config import settings

def sync_clerk_role(clerk_id: str):
    resp = httpx.patch(
        f"https://api.clerk.com/v1/users/{clerk_id}/metadata",
        headers={
            "Authorization": f"Bearer {settings.CLERK_SECRET_KEY}",
            "Content-Type": "application/json",
        },
        json={"public_metadata": {"role": "admin"}},
    )
    resp.raise_for_status()

def run(email: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"No user found with email {email}. "
                  f"Make sure they've signed up via Clerk first (so the webhook created their row).")
            return
        user.role = RoleEnum.admin
        db.commit()
        print(f"{email} is now an admin in the database.")
        try:
            sync_clerk_role(user.clerk_id)
            print(f"Clerk publicMetadata updated for {user.clerk_id}.")
        except httpx.HTTPStatusError as e:
            print(f"WARNING: DB updated but Clerk sync failed: {e.response.status_code} {e.response.text}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.promote_admin <email>")
        sys.exit(1)
    run(sys.argv[1])