# scripts/backfill_gallery_defaults.py
# Run once from the backend project root: python -m scripts.backfill_gallery_defaults
#
# The 9 baseline studio photos (center_1.jpeg..center_9.jpeg) were only ever
# a JS fallback in Home.jsx, shown while the gallery_images table was empty.
# The moment a photo got added through the admin dashboard, the table became
# non-empty, the frontend swapped from "show the JS fallback" to "show only
# what's in the DB", and the one new photo duplicated itself in the carousel
# loop effect (which is designed for many photos, not one).
#
# This inserts the 9 baseline photos as real rows (skipping any that are
# already present, so it's safe to run more than once) and pushes any
# photos already added through the dashboard to the end of the order, so
# nothing you've added gets lost or duplicated.

from app.db.database import SessionLocal
from app.db.models import GalleryImage

BASELINE = [
    ("/assets/center_1.jpeg", "The studio floor"),
    ("/assets/center_2.jpeg", "Reformer room"),
    ("/assets/center_3.jpeg", "Equipment wall"),
    ("/assets/center_4.jpeg", "Private coaching space"),
    ("/assets/center_5.jpeg", "Mat & stretch area"),
    ("/assets/center_6.jpeg", "Reception"),
    ("/assets/center_7.jpeg", "Studio detail"),
    ("/assets/center_8.jpeg", "Natural light corner"),
    ("/assets/center_9.jpeg", "Entrance"),
]
BASELINE_URLS = {url for url, _ in BASELINE}


def run():
    db = SessionLocal()
    try:
        existing = db.query(GalleryImage).all()
        existing_urls = {row.image_url for row in existing}

        added = 0
        for i, (url, caption) in enumerate(BASELINE):
            if url in existing_urls:
                continue
            db.add(GalleryImage(image_url=url, caption=caption, sort_order=i, is_active=True))
            added += 1

        # Anything already in the table that ISN'T one of the baseline photos
        # is something added through the dashboard — keep it, just move it
        # after the baseline block so ordering stays predictable.
        already_added = [row for row in existing if row.image_url not in BASELINE_URLS]
        for offset, row in enumerate(sorted(already_added, key=lambda r: r.sort_order)):
            row.sort_order = len(BASELINE) + offset

        db.commit()
        print(f"Added {added} baseline photo(s). {len(already_added)} previously-added photo(s) preserved and moved to the end.")
    finally:
        db.close()


if __name__ == "__main__":
    run()