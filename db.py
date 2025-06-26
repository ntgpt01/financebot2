from psycopg2.extras import RealDictCursor
import psycopg2
import pendulum
import os
from dotenv import load_dotenv
load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

def connect():
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)

def current_time():
    return pendulum.now("Asia/Ho_Chi_Minh").format("DD-MM HH:mm")

def get_accounts():
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM accounts ORDER BY id")
        return [row["name"] for row in cur.fetchall()]

def add_account(name):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO accounts (name) VALUES (%s) ON CONFLICT DO NOTHING", (name,))
        conn.commit()

def get_members():
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM members ORDER BY id")
        return [row["name"] for row in cur.fetchall()]

def add_member(name):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO members (name) VALUES (%s) ON CONFLICT DO NOTHING", (name,))
        conn.commit()

def save_transaction(type, account, member, amount):
    now = current_time()
    with connect() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO transactions (type, account, member, amount, time) VALUES (%s, %s, %s, %s, %s)",
            (type, account, member, amount, now)
        )
        conn.commit()

def get_transactions():
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, type, account, member, amount, time
            FROM transactions
            ORDER BY id
        """)
        return cur.fetchall()
