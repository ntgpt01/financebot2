import json
import psycopg2
from db import get_connection

with open("data/fund.json", "r", encoding="utf-8") as f:
    data = json.load(f)

conn = get_connection()
cur = conn.cursor()

# Insert members
for mem in data["members"]:
    cur.execute("INSERT INTO members (name) VALUES (%s) ON CONFLICT DO NOTHING", (mem,))

# Insert accounts
for acc in data["accounts"]:
    cur.execute("INSERT INTO accounts (name) VALUES (%s) ON CONFLICT DO NOTHING", (acc,))

# Insert transactions
for trans in data["transactions"]:
    cur.execute("""
        INSERT INTO transactions (type, account, amount, member, time)
        VALUES (%s, %s, %s, %s, %s)
    """, (trans["type"], trans["account"], trans["amount"], trans["member"], trans["time"]))

conn.commit()
cur.close()
conn.close()
print("✅ Đã chuyển dữ liệu từ fund.json vào PostgreSQL.")
