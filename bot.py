import os
import asyncio
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
HORDE_API_KEY = os.environ["HORDE_API_KEY"]  # Gerekiyorsa ekle
HORDE_URL = "https://stablehorde.net/api/v2/generate/async"

# --------------------------
# HORDE GÖRSEL ÜRETİMİ
# --------------------------
def generate_image(prompt):
    headers = {"apikey": HORDE_API_KEY}
    payload = {
        "prompt": prompt,
        "params": {"steps": 30},
        "nsfw": False
    }

    task = requests.post(HORDE_URL, json=payload, headers=headers).json()

    if "id" not in task:
        return None

    task_id = task["id"]

    # Task tamamlanana kadar bekle
    while True:
        status = requests.get(f"https://stablehorde.net/api/v2/generate/status/{task_id}").json()
        if status.get("done"):
            break
        asyncio.sleep(1)

    # Görsel URL'lerini çek
    result = requests.get(f"https://stablehorde.net/api/v2/generate/status/{task_id}").json()

    images = result.get("generations", [])
    if not images:
        return None

    return images[0]["img"]

# --------------------------
# TELEGRAM KOMUTLARI
# --------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hazırım efendim. Ne fotoğraf istersiniz?")

async def wallpaper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Efendim, görsel hazırlanıyor...")

    prompt = "4k fantasy landscape, colorful, beautiful light, ultra detailed"

    img_url = generate_image(prompt)

    if img_url is None:
        await update.message.reply_text("Efendim, görsel oluşturulamadı.")
        return

    await update.message.reply_photo(img_url)

# --------------------------
# ANA ÇALIŞMA (ASYNCIO.RUN KULLANILMAYACAK!)
# --------------------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("duvar", wallpaper))

    print("Bot çalışıyor...")
    app.run_polling()

if __name__ == "__main__":
    main()
