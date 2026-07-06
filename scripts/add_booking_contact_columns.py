from sqlalchemy import text
from app.db.database import engine

with engine.connect() as conn:
    conn.execute(text("ALTER TABLE bookings ADD COLUMN IF NOT EXISTS customer_phone VARCHAR;"))
    conn.execute(text("ALTER TABLE bookings ADD COLUMN IF NOT EXISTS customer_notes TEXT;"))
    conn.execute(text("ALTER TABLE bookings ADD COLUMN IF NOT EXISTS admin_notes VARCHAR;"))
    conn.commit()
    print("✅ customer_phone, customer_notes, admin_notes columns added to bookings table")