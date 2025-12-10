import os
import asyncio
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
HORDE_API_KEY = os.environ["HORDE_API_KEY"]
HORDE_URL = "https://stablehorde.net/api/v2/generate/async"


# --------------------------------------
# HORDE ÜRETİM FONKSİYONU
# --------------------------------------
async def horde_generate(prompt):
    # Kaliteyi otomatik yükselt
    prompt = (
        "masterpiece, best quality, ultra-detailed, 8k, hyper-realistic, cinematic lighting, "
        + prompt
    )

    headers = {"apikey": HORDE_API_KEY}
    payload = {
        "prompt": prompt,
        "params": {
            "steps": 40,
            "sampler_name": "k_euler",
            "cfg_scale": 9,
            "width": 768,
            "height": 768
        },
        "nsfw": False
    }

    # Görev oluştur
    task = requests.post(HORDE_URL, json=payload, headers=headers).json()
    if "id" not in task:
        return None

    task_id = task["id"]

    # Görev tamamlanana kadar döngü
    while True:
        status = requests.get(
            f"https://stablehorde.net/api/v2/generate/status/{task_id}"
        ).json()

        if status.get("done"):
            break

        await asyncio.sleep(2)

    # Sonuçları al
    result = requests.get(
        f"https://stablehorde.net/api/v2/generate/status/{task_id}"
    ).json()

    images = result.get("generations", [])
    if not images:
        return None

    return images[0]["img"]


# --------------------------------------
# KOMUTLAR
# --------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hazırım efendim. Görsel üretmek için /imagine yazıp konuyu belirtin.\n"
        "Örnek: /imagine red sky, floating island, ultra detail"
    )


async def duvar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Efendim, duvar kağıdı hazırlanıyor...")

    prompt = (
        "4k fantasy wallpaper, vivid colors, ultra-detailed scenery, magical atmosphere, "
        "cinematic light, beautiful landscape"
    )

    img = await horde_generate(prompt)

    if img is None:
        await update.message.reply_text("Görsel oluşturulamadı efendim.")
        return

    await update.message.reply_photo(img)


async def imagine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Efendim bir prompt belirtin. Örneğin:\n/imagine red sky")
        return

    prompt = " ".join(context.args)

    await update.message.reply_text("Efendim, görsel hazırlanıyor...")

    img = await horde_generate(prompt)

    if img is None:
        await update.message.reply_text("Görsel oluşturulamadı efendim.")
        return

    await update.message.reply_photo(img)


# --------------------------------------
# OTOMATİK PROMPT (normal mesaj)
# --------------------------------------
async def auto_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text.strip()

    await update.message.reply_text(f"Efendim, '{prompt}' için görsel hazırlanıyor...")

    img = await horde_generate(prompt)

    if img is None:
        await update.message.reply_text("Görsel oluşturulamadı efendim.")
        return

    await update.message.reply_photo(img)


# --------------------------------------
# ANA FONKSİYON
# --------------------------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("duvar", duvar))
    app.add_handler(CommandHandler("imagine", imagine))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_prompt))

    print("Bot çalışıyor...")
    app.run_polling()


if __name__ == "__main__":
    main()
