from sqlalchemy import text
from app.db.database import engine

with engine.connect() as conn:
    conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS address VARCHAR;"))
    conn.commit()
    print("address column added to users table")