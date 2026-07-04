from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserOut, UserUpdate
from app.crud import user as user_crud
from app.core.security import get_current_user, get_admin_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserOut)
def get_me(current_user=Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=UserOut)
def update_me(data: UserUpdate, current_user=Depends(get_current_user), db: Session=Depends(get_db)):
    return user_crud.update(db, current_user, data)

@router.delete("/me")
def delete_me(current_user=Depends(get_current_user), db: Session=Depends(get_db)):
    user_crud.delete(db, current_user)
    return {"detail": "Account deleted"}

@router.get("", response_model=list[UserOut])
def get_all_users(db: Session=Depends(get_db), _=Depends(get_admin_user)):
    return user_crud.get_all(db)