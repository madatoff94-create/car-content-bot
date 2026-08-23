# Car Content Bot — 0 so'm v0.1

Telegram'dagi `/cars today` buyrug'i -> Cloudflare Worker -> GitHub Actions ->
2 ta avtomobil uchun 12 slaydli 4K karusel + 2 ta 9:16 Reels -> Telegram.

## Day 1
1. Mercedes-AMG GT 63 S E PERFORMANCE
2. BMW M5 (G90)

## 0 so'm stack
- Telegram Bot API
- Cloudflare Workers Free
- GitHub Actions
- Wikimedia Commons rasmlari
- Python + Pillow
- FFmpeg

> Eslatma: Wikimedia rasmlari turli litsenziyalarda bo'ladi. `credits.txt`
> fayli har bir yuklangan rasm uchun manba va litsenziya ma'lumotlarini saqlaydi.

## 1. GitHub repo
Yangi PUBLIC repo yarating, masalan:
`car-content-bot`

ZIP ichidagi barcha fayllarni repoga yuklang.

## 2. Telegram bot
Telegram'da `@BotFather`:
- `/newbot`
- bot nomi va username bering
- BOT TOKEN'ni oling

Botga bir marta `/start` yuboring.

Tokenni chatga yoki GitHub kodiga yozmang.

## 3. GitHub Secrets
Repo -> Settings -> Secrets and variables -> Actions -> New repository secret

Kerak:
- `TELEGRAM_BOT_TOKEN`

`TELEGRAM_CHAT_ID` majburiy emas: `/cars today` webhook orqali kelganda chat_id workflow'ga uzatiladi.
Manual/scheduled run uchun qo'shishingiz mumkin.

## 4. GitHub PAT
Cloudflare Worker GitHub Actions'ni ishga tushirishi uchun fine-grained PAT yarating.
Faqat ushbu repo uchun:
- Contents: Read
- Actions: Read/Write
- Metadata: Read

Worker secret:
- `GITHUB_TOKEN`
- `GITHUB_OWNER`
- `GITHUB_REPO`
- `TELEGRAM_BOT_TOKEN`

## 5. Cloudflare Worker
`worker/index.js` faylini Cloudflare Worker'ga joylang.

Worker environment variables/secrets:
- GITHUB_TOKEN
- GITHUB_OWNER
- GITHUB_REPO
- TELEGRAM_BOT_TOKEN

Deploy qiling va Worker URL'ni oling, masalan:
`https://car-bot.YOUR.workers.dev`

## 6. Telegram webhook
Brauzerda quyidagini oching:

`https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=<WORKER_URL>`

Token va Worker URL'ni o'zingiznikiga almashtiring.

## 7. Ishlatish
Telegram botga:

`/cars today`

Bot darhol buyruq qabul qilinganini yozadi.
GitHub Actions kontentni yaratadi va Telegram'ga quyidagilarni yuboradi:
- `Mercedes..._carousel.zip`
- `Mercedes..._reel.mp4`
- `Mercedes..._caption.txt`
- `BMW..._carousel.zip`
- `BMW..._reel.mp4`
- `BMW..._caption.txt`

## Output
Karusel:
- 12 slayd
- 3840×4800
- JPG
- UZ/RU/EN qisqa ma'lumotlar

Reels:
- 1080×1920
- H.264 MP4
- ~18 soniya
- cinematic Ken Burns / zoom-pan
- musiqasiz; Instagram ichida trending audio qo'shish tavsiya qilinadi

## Manual test
GitHub -> Actions -> `Generate car content` -> Run workflow.

## Keyingi versiya
- 60 avtomobillik katalog
- avtomatik model rotatsiyasi
- 4K manba filtri
- 2K/4K reels master
- Instagram auto-post (API talablari bajarilganda)
