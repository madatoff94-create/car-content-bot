const GITHUB_OWNER = "madatoff94-create";
const GITHUB_REPO = "car-content-bot";
const WORKER_URL = "https://car-content-bot.madatoff94.workers.dev";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "GET" && url.pathname === "/setup-webhook") {
      const tg = await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/setWebhook`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          url: WORKER_URL,
          allowed_updates: ["message", "edited_message"],
          drop_pending_updates: true
        })
      });
      const body = await tg.text();
      return new Response(body, {
        status: tg.ok ? 200 : 500,
        headers: { "Content-Type": "application/json; charset=utf-8" }
      });
    }

    if (request.method === "GET" && url.pathname === "/webhook-info") {
      const tg = await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/getWebhookInfo`);
      const body = await tg.text();
      return new Response(body, {
        status: tg.ok ? 200 : 500,
        headers: { "Content-Type": "application/json; charset=utf-8" }
      });
    }

    if (request.method !== "POST") {
      return new Response("Car Content Bot webhook is alive.", { status: 200 });
    }

    let update;
    try {
      update = await request.json();
    } catch {
      return new Response("bad json", { status: 400 });
    }

    const message = update.message || update.edited_message;
    if (!message || !message.chat) return new Response("ok");

    const chatId = String(message.chat.id);
    const rawText = (message.text || "").trim();
    const text = rawText.toLowerCase();

    if (text === "/start") {
      await telegram(env, "sendMessage", {
        chat_id: chatId,
        text: "🚗 KARVON4K bot tayyor.\n\nV2 buyruq:\n/car BMW M5 F90\n\nEski buyruq:\n/cars today"
      });
      return new Response("ok");
    }

    if (text.startsWith("/car ")) {
      const model = rawText.slice(5).trim();
      if (!model) {
        await telegram(env, "sendMessage", {
          chat_id: chatId,
          text: "Mashina modelini yozing. Masalan: /car BMW M5 F90"
        });
        return new Response("ok");
      }

      await telegram(env, "sendMessage", {
        chat_id: chatId,
        text: `✅ V2 qabul qilindi.\n🚘 ${model}\n📸 15× premium 4K set\n🎬 1× cinematic Reel\n🔖 KARVON4K branding`
      });

      const gh = await dispatchGithub(env, "car_v2", { chat_id: chatId, model });
      if (!gh.ok) {
        const details = await gh.text();
        await telegram(env, "sendMessage", {
          chat_id: chatId,
          text: "❌ V2 workflow ishga tushmadi. GitHub tokenini tekshiring."
        });
        return new Response(details, { status: 500 });
      }
      return new Response("ok");
    }

    if (text === "/cars today" || text === "/cars_today" || text === "/cars") {
      await telegram(env, "sendMessage", {
        chat_id: chatId,
        text: "✅ Qabul qilindi. 2 ta 4K karusel + 2 ta Reels generatsiyasi ishga tushirildi."
      });

      const gh = await dispatchGithub(env, "cars_today", { chat_id: chatId });
      if (!gh.ok) {
        const details = await gh.text();
        await telegram(env, "sendMessage", {
          chat_id: chatId,
          text: "❌ GitHub workflow ishga tushmadi. GITHUB_TOKEN ni tekshiring."
        });
        return new Response(details, { status: 500 });
      }

      return new Response("ok");
    }

    await telegram(env, "sendMessage", {
      chat_id: chatId,
      text: "Buyruq: /car BMW M5 F90"
    });
    return new Response("ok");
  }
};

async function dispatchGithub(env, eventType, clientPayload) {
  return fetch(
    `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/dispatches`,
    {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${env.GITHUB_TOKEN}`,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "car-content-telegram-worker"
      },
      body: JSON.stringify({
        event_type: eventType,
        client_payload: clientPayload
      })
    }
  );
}

async function telegram(env, method, payload) {
  return fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/${method}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
}
