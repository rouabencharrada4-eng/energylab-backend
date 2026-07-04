# scripts/seed_services.py
# Run once from the backend project root: python -m scripts.seed_services
from app.db.database import SessionLocal
from app.db.models import Service

SERVICES = [
    dict(
        name="Private Coaching",
        description="One-on-one personal training tailored to your goals.",
        duration_minutes=60,
        max_capacity=1,
        requires_coach=True,
        is_active=True,
    ),
    dict(
        name="Pilates",
        description="Group or semi-private pilates sessions for strength and mobility.",
        duration_minutes=50,
        max_capacity=8,
        requires_coach=True,
        is_active=True,
    ),
    dict(
        name="Inbody Machine Service",
        description="Body composition scan session — no coach required.",
        duration_minutes=15,
        max_capacity=1,
        requires_coach=False,
        is_active=True,
    ),
]

def run():
    db = SessionLocal()
    try:
        existing_names = {s.name for s in db.query(Service).all()}
        added = 0
        for data in SERVICES:
            if data["name"] in existing_names:
                print(f"skip (already exists): {data['name']}")
                continue
            db.add(Service(**data))
            added += 1
            print(f"added: {data['name']}")
        db.commit()
        print(f"Done. {added} service(s) added.")
    finally:
        db.close()

if __name__ == "__main__":
    run()