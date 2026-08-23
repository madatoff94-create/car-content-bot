import json, os
from pathlib import Path
import requests

TOKEN=os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID=os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get("TARGET_CHAT_ID")
if not CHAT_ID: raise SystemExit("No TELEGRAM_CHAT_ID/TARGET_CHAT_ID supplied.")
BASE=f"https://api.telegram.org/bot{TOKEN}"

def msg(text):
    r=requests.post(BASE+"/sendMessage",data={"chat_id":CHAT_ID,"text":text},timeout=60); r.raise_for_status()

def doc(path, caption=None):
    with open(path,"rb") as f:
        r=requests.post(BASE+"/sendDocument",data={"chat_id":CHAT_ID,"caption":caption or ""},files={"document":f},timeout=180)
    r.raise_for_status()

def video(path, caption=None):
    with open(path,"rb") as f:
        r=requests.post(BASE+"/sendVideo",data={"chat_id":CHAT_ID,"caption":caption or "","supports_streaming":"true"},files={"video":f},timeout=300)
    r.raise_for_status()

cars=json.loads(Path("data/cars.json").read_text(encoding="utf-8"))
msg("✅ Bugungi 2 ta avtomobil kontent paketi tayyor.")
for car in cars:
    base=Path("work")/car["slug"]
    doc(base/f"{car['slug']}_carousel.zip",f"📸 {car['name']} — 12× 4K carousel")
    video(base/f"{car['slug']}_reel.mp4",f"🎬 {car['name']} — Reels 9:16")
    doc(base/f"{car['slug']}_caption.txt",f"📝 {car['name']} — UZ/RU/EN caption")
    cr=base/f"{car['slug']}_image_credits.txt"
    if cr.exists(): doc(cr,f"©️ {car['name']} — image licenses/sources")
msg("🚀 Tayyor. Instagram'ga joylash mumkin.")
