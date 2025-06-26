# from aiogram import Bot, Dispatcher
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
# from aiogram.utils import executor
# from config import TELEGRAM_TOKEN
# from handlers import register_handlers

# bot = Bot(token=TELEGRAM_TOKEN)  # ✅ Dùng đúng biến đã import
# storage = MemoryStorage()
# dp = Dispatcher(bot, storage=storage)

# register_handlers(dp)

# if __name__ == "__main__":
#     executor.start_polling(dp, skip_updates=True)


# bot.py
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import Update
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

@app.route(WEBHOOK_PATH, methods=["POST"])
# async def webhook():
#     request_data = request.get_json()
#     update = Update(**request_data)
#     await dp.process_update(update)
#     return "ok"
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    try:
        request_data = request.get_json()
        update = Update(**request_data)
        import asyncio
        asyncio.run(dp.process_update(update))
        return "✅ Update processed", 200
    except Exception as e:
        return f"❌ Error in webhook: {str(e)}", 500

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
