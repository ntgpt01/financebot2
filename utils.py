# utils.py
import json
import os
from datetime import datetime
import pendulum

FUND_FILE = "data/fund.json"

def load_fund():
    if not os.path.exists(FUND_FILE):
        os.makedirs(os.path.dirname(FUND_FILE), exist_ok=True)
        return {"accounts": [], "members": [], "transactions": []}
    with open(FUND_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_fund(data):
    os.makedirs(os.path.dirname(FUND_FILE), exist_ok=True)  # 🔐 tạo thư mục nếu thiếu
    with open(FUND_FILE, "w", encoding="utf-8") as f:
        f.write('{\n  "accounts": ' + json.dumps(data["accounts"], ensure_ascii=False) + ',\n')
        f.write('  "members": ' + json.dumps(data["members"], ensure_ascii=False) + ',\n')
        f.write('  "transactions": [\n')
        for i, t in enumerate(data["transactions"]):
            line = json.dumps(t, ensure_ascii=False, separators=(',', ':'))
            comma = ',' if i < len(data["transactions"]) - 1 else ''
            f.write(f"    {line}{comma}\n")
        f.write('  ]\n}')

def current_time():
    now = pendulum.now("Asia/Ho_Chi_Minh")
    formatted = now.format("DD-MM HH:mm")
    print("✅ current_time:", formatted)
    return formatted
