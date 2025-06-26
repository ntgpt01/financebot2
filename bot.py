

# bot.py
import os
from aiogram.types import Update  # ✅ phải đặt trước khi dùng
print("✅ Update class from:", Update.__module__)
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from handlers import register_handlers
from config import TELEGRAM_TOKEN
from flask import Flask, request
bot = Bot(token=TELEGRAM_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

register_handlers(dp)

WEBHOOK_PATH = f"/{TELEGRAM_TOKEN}"
WEBHOOK_URL = f"https://financebot2.onrender.com{WEBHOOK_PATH}"

app = Flask(__name__)
@app.route("/", methods=["GET"])
def index():
    return "FinanceBot is alive!"


from aiogram import types
from aiogram import Bot, Dispatcher

from aiogram import types
from aiogram import Bot, Dispatcher

@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    import asyncio
    import json
    import traceback

    try:
        request_data = request.get_json(force=True)
        print("🔥 Webhook received:", json.dumps(request_data, indent=2))
        
        update = types.Update(**request_data)

        # ✅ Set current instance để tránh lỗi context
        Bot.set_current(bot)
        Dispatcher.set_current(dp)

        asyncio.run(dp.process_update(update))
        return "✅ Update processed", 200

    except Exception as e:
        print("❌ Webhook error:\n", traceback.format_exc())
        return "❌ Error in webhook", 500

@app.route("/setwebhook", methods=["GET"])
def set_webhook():
    import asyncio
    try:
        asyncio.run(bot.set_webhook(WEBHOOK_URL))
        return f"✅ Webhook đã được set về: {WEBHOOK_URL}"
    except Exception as e:
        return f"❌ Lỗi khi set webhook: {str(e)}"



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
