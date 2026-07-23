import logging
import jwt
from jwt import PyJWKClient
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.database import get_db
from app.crud import user as user_crud
from app.schemas.user import UserCreate
from app.core.config import settings

log = logging.getLogger("auth")

bearer_scheme = HTTPBearer()

_jwks_clients: dict[str, PyJWKClient] = {}

def _get_jwks_client(issuer: str) -> PyJWKClient:
    if issuer not in _jwks_clients:
        _jwks_clients[issuer] = PyJWKClient(f"{issuer}/.well-known/jwks.json")
    return _jwks_clients[issuer]

# app/core/security.py
import logging

logger = logging.getLogger(__name__)

# app/core/security.py
async def get_clerk_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    token = credentials.credentials
    try:
        unverified = jwt.decode(token, options={"verify_signature": False})
        issuer = unverified.get("iss")
        if not issuer:
            raise HTTPException(status_code=401, detail="Missing issuer")

        print(f"[AUTH] issuer={issuer}")
        print(f"[AUTH] token_preview={token[:40]}...")

        jwks_client = _get_jwks_client(issuer)
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_exp": True},
            leeway=30,          # ← 30-second tolerance for clock skew
        )
        print(f"[AUTH] OK sub={payload['sub']}")
        return payload["sub"]

    except jwt.ExpiredSignatureError:
        print("[AUTH] FAIL: token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        print(f"[AUTH] FAIL InvalidTokenError: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"[AUTH] FAIL {type(e).__name__}: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


async def _fetch_and_create_user_from_clerk(db: Session, clerk_id: str):
    """Self-healing fallback for when the `user.created` webhook hasn't
    landed yet — or never will, e.g. a stale ngrok tunnel in local dev, or
    a missed delivery in production. Pulls the user straight from Clerk's
    API instead of leaving them stuck waiting on a webhook that may never
    arrive."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://api.clerk.com/v1/users/{clerk_id}",
                headers={"Authorization": f"Bearer {settings.CLERK_SECRET_KEY}"},
                timeout=10,
            )
        if resp.status_code != 200:
            print(f"[AUTH] Clerk API fallback fetch failed: status={resp.status_code}")
            return None
        data = resp.json()
    except Exception as e:
        print(f"[AUTH] Clerk API fallback fetch errored: {e}")
        return None

    email_addresses = data.get("email_addresses", [])
    primary_email_id = data.get("primary_email_address_id")
    email = next(
        (e["email_address"] for e in email_addresses if e["id"] == primary_email_id),
        email_addresses[0]["email_address"] if email_addresses else None,
    )
    if not email:
        return None

    full_name = f"{data.get('first_name', '')} {data.get('last_name', '')}".strip() or email
    metadata = data.get("unsafe_metadata", {}) or {}

    try:
        return user_crud.create(db, UserCreate(
            clerk_id=clerk_id,
            email=email,
            full_name=full_name,
            phone=metadata.get("phone") or None,
            address=metadata.get("address") or None,
        ))
    except IntegrityError:
        # Lost a race with the webhook (or another concurrent request) —
        # someone else just created this same row, so just fetch it.
        db.rollback()
        return user_crud.get_by_clerk_id(db, clerk_id)


async def get_current_user(
    clerk_id: str = Depends(get_clerk_user_id),
    db: Session = Depends(get_db),
):
    user = user_crud.get_by_clerk_id(db, clerk_id)
    if not user:
        user = await _fetch_and_create_user_from_clerk(db, clerk_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found — sync may be pending")
    return user

async def get_admin_user(current_user=Depends(get_current_user)):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user