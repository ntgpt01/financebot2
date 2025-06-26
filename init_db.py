import psycopg2

DB_URL = "postgresql://ntknguyen:C9OoPKUa37OedMJgA3Ny9zpOkv6cLvB4@dpg-d1ep61h5pdvs73d1c7m0-a.singapore-postgres.render.com/financebot_db_qxpe"

create_table_sql = """
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS members (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    type TEXT CHECK (type IN ('Thu', 'Chi')) NOT NULL,
    account TEXT NOT NULL,
    member TEXT NOT NULL,
    amount INTEGER NOT NULL,
    time TEXT NOT NULL
);
"""

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()
cur.execute(create_table_sql)
conn.commit()
cur.close()
conn.close()
print("✅ Đã tạo bảng thành công.")
