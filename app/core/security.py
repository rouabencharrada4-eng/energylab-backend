import jwt
import httpx
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.db.database import get_db
from app.crud import user as user_crud
from sqlalchemy.orm import Session

bearer_scheme = HTTPBearer()

# Cache the JWKS client per issuer to avoid refetching on every request
_jwks_clients: dict[str, PyJWKClient] = {}

def _get_jwks_client(issuer: str) -> PyJWKClient:
    if issuer not in _jwks_clients:
        _jwks_clients[issuer] = PyJWKClient(f"{issuer}/.well-known/jwks.json")
    return _jwks_clients[issuer]

async def get_clerk_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    token = credentials.credentials
    try:
        # Decode header only to get issuer for JWKS lookup
        unverified = jwt.decode(token, options={"verify_signature": False})
        issuer = unverified.get("iss")
        if not issuer:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: missing issuer")

        jwks_client = _get_jwks_client(issuer)
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_exp": True},
        )
        return payload["sub"]

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

async def get_current_user(
    clerk_id: str = Depends(get_clerk_user_id),
    db: Session = Depends(get_db),
):
    user = user_crud.get_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found — sync may be pending")
    return user

async def get_admin_user(current_user=Depends(get_current_user)):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user