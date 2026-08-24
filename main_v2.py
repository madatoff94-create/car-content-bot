import json
import os
import re
from pathlib import Path

import requests

MODEL = (os.environ.get("CAR_MODEL") or "").strip()
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TARGET_CHAT_ID") or os.environ.get("TELEGRAM_CHAT_ID")

if not MODEL:
    raise SystemExit("CAR_MODEL is required for V2. Example: BMW M5 F90")

LOCATIONS = [
    {"city": "Dushanbe", "location": "Ismoil Somoniy Monument"},
    {"city": "Khujand", "location": "Kamoli Khujandi park / Syr Darya promenade"},
    {"city": "Tashkent", "location": "Tashkent City"},
    {"city": "Samarkand", "location": "Registan panorama"},
    {"city": "Bukhara", "location": "Poi Kalon panorama"},
]

# Stable model -> one city/location mapping without a database.
idx = sum(ord(c) for c in MODEL.lower()) % len(LOCATIONS)
loc = LOCATIONS[idx]

slug = re.sub(r"[^a-z0-9]+", "-", MODEL.lower()).strip("-")
out = Path("work") / f"v2-{slug}"
out.mkdir(parents=True, exist_ok=True)

manifest = {
    "version": "2.0",
    "brand": "KARVON4K",
    "model": MODEL,
    "color": "black",
    "city": loc["city"],
    "location": loc["location"],
    "image_count": 15,
    "master_format": "4K vertical",
    "reel": {
        "format": "9:16",
        "target": "2160x3840",
        "duration_seconds": 20,
        "style": "premium cinematic",
    },
    "shots": [
        "front 3/4 hero",
        "front centered",
        "side profile",
        "rear 3/4",
        "rear centered",
        "wide establishing hero",
        "wheel and brake detail",
        "headlight / body detail",
        "interior cockpit",
        "interior dashboard and steering",
        "front seats and center console",
        "rear seats",
        "engine bay",
        "full underbody",
        "suspension / brake / exhaust technical detail",
    ],
    "plate_text": "KARVON4K",
    "rules": [
        "same exact car in every frame",
        "same black exterior color",
        "same wheel design and trim",
        "same city and same landmark area",
        "no overlay text or watermark",
        "photorealistic premium automotive photography",
        "KARVON4K plate on exterior shots",
    ],
}

(out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

if TOKEN and CHAT_ID:
    text = (
        "🚘 KARVON4K V2 request tayyor\n"
        f"Model: {MODEL}\n"
        f"Rang: Black\n"
        f"Joy: {loc['city']} — {loc['location']}\n"
        "📸 15× 4K premium shot plan\n"
        "🎬 4K vertical cinematic Reel plan\n\n"
        "⚙️ V2 image-generation backend ulanish bosqichida."
    )
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text},
        timeout=60,
    )
    r.raise_for_status()

print(json.dumps(manifest, ensure_ascii=False, indent=2))
