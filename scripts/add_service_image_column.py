from sqlalchemy import text
from app.db.database import engine

with engine.connect() as conn:
    conn.execute(text("ALTER TABLE services ADD COLUMN IF NOT EXISTS image_url VARCHAR;"))
    conn.commit()
    print("✅ image_url column added to services table")