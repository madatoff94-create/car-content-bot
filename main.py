import subprocess, sys, os
steps=[
    ["python","-m","src.fetch_images"],
    ["python","-m","src.render_carousel"],
    ["python","-m","src.render_reels"],
]
for cmd in steps:
    print("RUN:", " ".join(cmd), flush=True)
    subprocess.run(cmd,check=True)
if os.environ.get("TELEGRAM_BOT_TOKEN") and (os.environ.get("TARGET_CHAT_ID") or os.environ.get("TELEGRAM_CHAT_ID")):
    subprocess.run(["python","-m","src.telegram_send"],check=True)
else:
    print("Telegram secrets/chat id not supplied; generated files are in work/.")
