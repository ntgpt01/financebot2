#!/bin/bash
# Giả vờ mở cổng cho Render vui
python web_dummy.py &

# Chạy bot Telegram như thường
python bot.py
