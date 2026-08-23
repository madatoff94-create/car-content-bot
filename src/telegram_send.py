import json
import os
from pathlib import Path

import requests

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get("TARGET_CHAT_ID")
if not CHAT_ID:
    raise SystemExit("No TELEGRAM_CHAT_ID/TARGET_CHAT_ID supplied.")

BASE = f"https://api.telegram.org/bot{TOKEN}"
MAX_UPLOAD = 49 * 1024 * 1024  # stay below Telegram Bot API's 50 MB limit


def msg(text):
    r = requests.post(
        BASE + "/sendMessage",
        data={"chat_id": CHAT_ID, "text": text},
        timeout=60,
    )
    r.raise_for_status()


def doc(path, caption=None):
    path = Path(path)
    if path.stat().st_size > MAX_UPLOAD:
        raise ValueError(f"File too large for Telegram Bot API: {path}")
    with open(path, "rb") as f:
        r = requests.post(
            BASE + "/sendDocument",
            data={"chat_id": CHAT_ID, "caption": caption or ""},
            files={"document": (path.name, f)},
            timeout=300,
        )
    r.raise_for_status()


def video(path, caption=None):
    path = Path(path)
    if path.stat().st_size > MAX_UPLOAD:
        raise ValueError(f"Video too large for Telegram Bot API: {path}")
    with open(path, "rb") as f:
        r = requests.post(
            BASE + "/sendVideo",
            data={
                "chat_id": CHAT_ID,
                "caption": caption or "",
                "supports_streaming": "true",
            },
            files={"video": (path.name, f)},
            timeout=600,
        )
    r.raise_for_status()


def send_carousel(base, car):
    zip_path = base / f"{car['slug']}_carousel.zip"
    if zip_path.exists() and zip_path.stat().st_size <= MAX_UPLOAD:
        doc(zip_path, f"📸 {car['name']} — 12× 4K carousel ZIP")
        return

    # Preserve full 4K quality by sending each slide as a document if the ZIP
    # is larger than Telegram's standard Bot API upload limit.
    slides = sorted((base / "carousel").glob("*.jpg"))
    msg(
        f"📸 {car['name']} — ZIP 50 MB limitdan katta. "
        f"{len(slides)} ta 4K slayd original sifatda alohida yuboriladi."
    )
    for i, slide in enumerate(slides, 1):
        doc(slide, f"{car['name']} — 4K carousel {i:02d}/{len(slides):02d}")


cars = json.loads(Path("data/cars.json").read_text(encoding="utf-8"))
msg("✅ Bugungi 2 ta avtomobil kontent paketi tayyor.")

for car in cars:
    base = Path("work") / car["slug"]
    send_carousel(base, car)
    video(base / f"{car['slug']}_reel.mp4", f"🎬 {car['name']} — Reels 9:16")
    doc(base / f"{car['slug']}_caption.txt", f"📝 {car['name']} — UZ/RU/EN caption")
    cr = base / f"{car['slug']}_image_credits.txt"
    if cr.exists():
        doc(cr, f"©️ {car['name']} — image licenses/sources")

msg("🚀 Tayyor. Instagram'ga joylash mumkin.")
