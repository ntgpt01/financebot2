import os
import json
from datetime import datetime
import pendulum
import inspect

# ✅ Đường dẫn tuyệt đối đến fund.json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FUND_FILE = os.path.join(BASE_DIR, "data", "fund.json")

def load_fund():
    caller = inspect.stack()[1].function
    print(f"🔍 load_fund() được gọi từ: {caller}")
    print("📂 Đang load fund từ:", FUND_FILE)

    if not os.path.exists(FUND_FILE):
        print("⚠️ File không tồn tại, trả về dữ liệu trống.")
        os.makedirs(os.path.dirname(FUND_FILE), exist_ok=True)
        return {"accounts": [], "members": [], "transactions": []}

    with open(FUND_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            print("✅ Đã load fund.json thành công.")
            print("📦 Dữ liệu:", json.dumps(data, indent=2, ensure_ascii=False))
            return data
        except Exception as e:
            print("❌ Lỗi đọc fund.json:", e)
            return {"accounts": [], "members": [], "transactions": []}

def save_fund(data):
    os.makedirs(os.path.dirname(FUND_FILE), exist_ok=True)
    with open(FUND_FILE, "w", encoding="utf-8") as f:
        f.write('{\n  "accounts": ' + json.dumps(data["accounts"], ensure_ascii=False) + ',\n')
        f.write('  "members": ' + json.dumps(data["members"], ensure_ascii=False) + ',\n')
        f.write('  "transactions": [\n')
        for i, t in enumerate(data["transactions"]):
            line = json.dumps(t, ensure_ascii=False, separators=(',', ':'))
            comma = ',' if i < len(data["transactions"]) - 1 else ''
            f.write(f"    {line}{comma}\n")
        f.write('  ]\n}')
    print("📝 Đang ghi fund.json tại:", FUND_FILE)

def current_time():
    now = pendulum.now("Asia/Ho_Chi_Minh")
    formatted = now.format("DD-MM HH:mm")
    print("✅ current_time:", formatted)
    return formatted
