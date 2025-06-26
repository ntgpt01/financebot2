# bot.py
import os
import asyncio
import json
import traceback
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TELEGRAM_TOKEN
from bot_handlers.handlers import register_handlers


# ✅ Khởi tạo bot & dispatcher
bot = Bot(token=TELEGRAM_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
register_handlers(dp)

# ✅ Thông tin webhook
WEBHOOK_PATH = f"/{TELEGRAM_TOKEN}"
WEBHOOK_URL = f"https://financebot2.onrender.com{WEBHOOK_PATH}"

# ✅ Flask app
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "FinanceBot is alive!"

@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    try:
        request_data = request.get_json(force=True)
        print("🔥 Webhook received:", json.dumps(request_data, indent=2))

        update = types.Update(**request_data)
        Bot.set_current(bot)
        Dispatcher.set_current(dp)

        asyncio.run(dp.process_update(update))
        return "✅ Update processed", 200

    except Exception as e:
        print("❌ Webhook error:\n", traceback.format_exc())
        return "❌ Error in webhook", 500

@app.route("/setwebhook", methods=["GET"])
def set_webhook():
    try:
        asyncio.run(bot.set_webhook(WEBHOOK_URL))
        return f"✅ Webhook đã được set về: {WEBHOOK_URL}"
    except Exception as e:
        return f"❌ Lỗi khi set webhook: {str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
