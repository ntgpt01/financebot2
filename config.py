import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if TELEGRAM_TOKEN is None:
    raise Exception("TELEGRAM_TOKEN is not set in environment variables.")
