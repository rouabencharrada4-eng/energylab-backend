# scripts/promote_admin.py
# Run once: python -m scripts.promote_admin someone@example.com
import sys
from app.db.database import SessionLocal
from app.db.models import User, RoleEnum

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
        print(f"{email} is now an admin.")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.promote_admin <email>")
        sys.exit(1)
    run(sys.argv[1])