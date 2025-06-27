import sqlite3

# ⚠️ Thay đường dẫn nếu file fund.db không nằm cùng thư mục
conn = sqlite3.connect('fund.db')
cursor = conn.cursor()

# 🗑 Xoá toàn bộ giao dịch trong bảng transactions
cursor.execute("DELETE FROM transactions")

# 🔁 Reset lại ID tự tăng nếu bạn muốn ID bắt đầu lại từ 1
cursor.execute("DELETE FROM sqlite_sequence WHERE name='transactions'")

conn.commit()
conn.close()

print("✅ Đã xoá toàn bộ lịch sử giao dịch Quỹ.")
