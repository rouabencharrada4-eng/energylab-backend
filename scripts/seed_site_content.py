# scripts/seed_site_content.py
# Run once from the backend project root: python -m scripts.seed_site_content
#
# Populates site_content / gallery_images / showcase_items with the copy and
# images that used to be hardcoded in the frontend, so the homepage looks
# identical the moment this ships — the admin can then edit everything from
# the dashboard.

from app.db.database import SessionLocal
from app.db.models import SiteContent, GalleryImage, ShowcaseItem

SITE_CONTENT = {
    "hero_title_line1": "Energy",
    "hero_title_line2": "Lab",
    "hero_tagline": "Fitness · Wellness · Pilates",
    "hero_bg_url": "/assets/hero-bg.jpg",
    "logo_url": "/assets/logo-mark.png",

    "about_heading": "About Us",
    "about_text": "\n\n".join([
        "Welcome to Energy Lab—a space where movement, wellness, and mindfulness come together.",
        "We believe true strength is built through intention, not intensity. Every Pilates session is thoughtfully designed around controlled movement and mindful breathing, helping you strengthen your body, improve mobility, and cultivate lasting balance.",
        "From private coaching and group classes to InBody assessments, every experience is tailored to support your individual journey. Our studio offers a peaceful, modern environment where you can disconnect from the pace of everyday life and reconnect with yourself.",
        "At Energy Lab, wellness isn't just a workout—it's a way of living.",
    ]),

    "space_heading": "Our Space",
    "space_subheading": "A quiet, modern studio designed for focus — here's a glimpse before you visit.",

    "contact_location": "Tunis, Lafayette 5020",
    "contact_phone": "55 555 555",
    "contact_email": "energylab-contact@gmail.com",
    "map_query": "Tunis, Lafayette 5020, Tunisia",
}

GALLERY = [
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

SHOWCASE = [
    dict(
        name="Private Coaching",
        image_url="/assets/card_1.png",
        description="Strength, conditioning, or a mix of both — a dedicated coach designs every session around your goals and pace.",
        align="left",
        bookable=True,
    ),
    dict(
        name="Inbody Machine Service",
        image_url="/assets/card_3.png",
        description="Precise body composition scans that track real progress — muscle, fat, water — far beyond what a scale can tell you.",
        align="right",
        bookable=False,
    ),
    dict(
        name="Pilates",
        image_url="/assets/card_2.png",
        description="Mat and reformer sessions focused on controlled movement, flexibility, and a stronger core.",
        align="left",
        bookable=True,
    ),
]


def run():
    db = SessionLocal()
    try:
        # --- site content ---
        existing_keys = {row.key for row in db.query(SiteContent).all()}
        added = 0
        for key, value in SITE_CONTENT.items():
            if key in existing_keys:
                continue
            db.add(SiteContent(key=key, value=value))
            added += 1
        print(f"site_content: {added} key(s) added, {len(existing_keys)} already present.")

        # --- gallery ---
        if db.query(GalleryImage).count() == 0:
            for i, (src, caption) in enumerate(GALLERY):
                db.add(GalleryImage(image_url=src, caption=caption, sort_order=i, is_active=True))
            print(f"gallery_images: {len(GALLERY)} added.")
        else:
            print("gallery_images: already has rows, skipping.")

        # --- showcase ---
        if db.query(ShowcaseItem).count() == 0:
            for i, item in enumerate(SHOWCASE):
                db.add(ShowcaseItem(sort_order=i, is_active=True, **item))
            print(f"showcase_items: {len(SHOWCASE)} added.")
        else:
            print("showcase_items: already has rows, skipping.")

        db.commit()
        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    run()