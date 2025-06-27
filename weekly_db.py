import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
load_dotenv()

DB_URL = os.getenv("DB_URL")

def connect():
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)

def get_weekly_info():
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name, rate FROM weekly_info ORDER BY id")
        rows = cur.fetchall()
        # Trả ra dict: {name: {rate: x}}
        return {row["name"]: {"rate": row["rate"]} for row in rows}

def insert_weekly_report(week_key, person, amount, rate, tientuan):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO weekly_reports (week_key, person, amount, rate, tientuan)
            VALUES (%s, %s, %s, %s, %s)
        """, (week_key, person, amount, rate, tientuan))
        conn.commit()

def get_weekly_report(week_key):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, week_key, person, amount, rate, tientuan
            FROM weekly_reports
            WHERE week_key = %s
            ORDER BY id
        """, (week_key,))
        return cur.fetchall()

def get_all_weeks():
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT week_key, SUM(tientuan) as total
            FROM weekly_reports
            GROUP BY week_key
            ORDER BY week_key DESC
        """)
        return cur.fetchall()
