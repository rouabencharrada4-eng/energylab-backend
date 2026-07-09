# scripts/migrate_about_text.py
# Run once from the backend project root: python -m scripts.migrate_about_text
#
# The About section used to be 4 separate paragraph fields
# (about_paragraph_1..4) plus an admin-uploaded about_image_url. It's now a
# single about_text field, and the image is fixed in code (about_us.png).
# This combines whatever paragraph content is currently in the DB into
# about_text (so nothing you'd already typed gets lost), then removes the
# now-unused keys.

from app.db.database import SessionLocal
from app.db.models import SiteContent

PARAGRAPH_KEYS = ["about_paragraph_1", "about_paragraph_2", "about_paragraph_3", "about_paragraph_4"]
KEYS_TO_DROP = PARAGRAPH_KEYS + ["about_image_url"]


def run():
    db = SessionLocal()
    try:
        rows = {row.key: row for row in db.query(SiteContent).filter(SiteContent.key.in_(PARAGRAPH_KEYS)).all()}
        paragraphs = [rows[k].value.strip() for k in PARAGRAPH_KEYS if k in rows and rows[k].value.strip()]

        existing_about_text = db.query(SiteContent).filter(SiteContent.key == "about_text").first()
        if existing_about_text:
            print("about_text already exists — leaving it alone, not overwriting.")
        elif paragraphs:
            db.add(SiteContent(key="about_text", value="\n\n".join(paragraphs)))
            print(f"about_text created from {len(paragraphs)} existing paragraph(s).")
        else:
            print("No existing paragraph content found — nothing to migrate (default will be used).")

        dropped = 0
        for key in KEYS_TO_DROP:
            row = db.query(SiteContent).filter(SiteContent.key == key).first()
            if row:
                db.delete(row)
                dropped += 1
        print(f"Removed {dropped} unused key(s).")

        db.commit()
        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    run()