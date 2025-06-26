from psycopg2.extras import RealDictCursor
import psycopg2
import pendulum
import os
from dotenv import load_dotenv
load_dotenv()


   
def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)



DB_URL = "postgresql://ntknguyen:C9OoPKUa37OedMJgA3Ny9zpOkv6cLvB4@dpg-d1ep61h5pdvs73d1c7m0-a/financebot_db_qxpe"

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
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM accounts WHERE name = %s", (account,))
        account_id = cur.fetchone()["id"]
        cur.execute("SELECT id FROM members WHERE name = %s", (member,))
        member_id = cur.fetchone()["id"]
        cur.execute(
            "INSERT INTO transactions (type, account_id, member_id, amount, time) VALUES (%s, %s, %s, %s, %s)",
            (type, account_id, member_id, amount, current_time())
        )
        conn.commit()

def get_transactions():
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT t.id, t.type, a.name AS account, m.name AS member, t.amount, t.time
            FROM transactions t
            JOIN accounts a ON t.account_id = a.id
            JOIN members m ON t.member_id = m.id
            ORDER BY t.id
        """)
        return cur.fetchall()
