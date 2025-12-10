import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
HORDE_API_KEY = os.environ.get("HORDE_API_KEY")

if not TOKEN:
    raise Exception("BOT_TOKEN eksik!")
if not HORDE_API_KEY:
    raise Exception("HORDE_API_KEY eksik!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Merhaba! Bir görüntü üretmek için /imagine komutunu kullanın.\n\nÖrnek:\n"
        "/imagine güneşli bir sahil, yüksek kalite"
    )

async def imagine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Lütfen bir açıklama girin. Örnek:\n/imagine mavi ejderha, detallı")
        return

    prompt = " ".join(context.args)
    await update.message.reply_text("Görsel üretiliyor, lütfen bekleyin...")

    # HORDE API
    payload = {
        "prompt": prompt,
        "params": {
            "sampler_name": "k_euler",
            "width": 512,
            "height": 512,
            "steps": 25
        },
        "nsfw": False
    }

    headers = {
        "apikey": HORDE_API_KEY,
        "Client-Agent": "telegram-bot"
    }

    task = requests.post("https://stablehorde.net/api/v2/generate/async", json=payload, headers=headers).json()

    if "id" not in task:
        await update.message.reply_text(f"Üretim başlatılamadı:\n{task}")
        return

    task_id = task["id"]

    # Sonucu takip et
    while True:
        check = requests.get(f"https://stablehorde.net/api/v2/generate/status/{task_id}").json()
        if check.get("done"):
            break

    # Gösterilen görseli al
    if not check["generations"]:
        await update.message.reply_text("Görsel üretimi başarısız oldu.")
        return

    image_url = check["generations"][0]["img"]

    await update.message.reply_photo(image_url)

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("imagine", imagine))

    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
