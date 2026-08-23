# SETUP CHECKLIST

1. GitHub'da PUBLIC `car-content-bot` repo yarating.
2. Ushbu ZIP fayllarini repoga upload qiling.
3. Telegram @BotFather'da bot yarating va token oling.
4. GitHub Actions Secret: TELEGRAM_BOT_TOKEN.
5. GitHub fine-grained PAT yarating (faqat ushbu repo, Actions write).
6. Cloudflare Worker yarating, `worker/index.js` ni joylang.
7. Worker secrets:
   - TELEGRAM_BOT_TOKEN
   - GITHUB_TOKEN
   - GITHUB_OWNER
   - GITHUB_REPO
8. Worker deploy.
9. Telegram setWebhook orqali Worker URL'ni ulang.
10. Botga `/cars today` yuboring.
