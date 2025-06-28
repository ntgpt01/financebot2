from db import connect  # hoặc from weekly_db import connect

def run_init():
    th04_data = [
        ("Khang", "TH04", 40),
        ("Trung", "TH04", 50),
        ("TH 001", "TH04", 50),
        ("TH 002", "TH04", 50),
        ("TH 003", "TH04", 50),
        ("TH 004", "TH04", 50),
        ("TH 005", "TH04", 50),
        ("TH 006", "TH04", 50),
        ("Aha Khang", "TH04", 55),
        ("Dieu(Khang)", "TH04", 55),
        ("Duy Khang", "TH04", 50),
        ("Khang Ut 2", "TH04", 50),
        ("Ut Khang", "TH04", 60),
    ]

    th01_data = [
        ("Co Huong", "TH01", 0),
        ("Goem", "TH01", 0),
        ("Huyền", "TH01", 0),
        ("Hieu", "TH01", 0),
        ("Vũ", "TH01", 25),
        ("Lâm Bình", "TH01", 0),
        ("Tu", "TH01", 0),
        ("Vk Gau", "TH01", 0),
        ("Thuy", "TH01", 0),
        ("Bi", "TH01", 0),
        ("Atha", "TH01", 10),
    ]

    th02_data = [
        ("Family", "TH02", 35),
        ("Vinh", "TH02", 50),
        ("A6. A Tuan", "TH02", 30),
        ("ALiem", "TH02", 35),
        ("CHang", "TH02", 35),
        ("ASang", "TH02", 20),
        ("A6.4", "TH02", 20),
        ("A6.usa", "TH02", 40),
        ("A6.2", "TH02", 40),
        ("A6.3", "TH02", 40),
        ("Phung D", "TH02", 40),
        ("Tuan(Vani)", "TH02", 30),
    ]
    th04_data = [
        ("Khang", "TH04", 40),
        ("Trung", "TH04", 50),
        ("TH 001", "TH04", 50),
        ("TH 002", "TH04", 50),
        ("TH 003", "TH04", 50),
        ("TH 004", "TH04", 50),
        ("TH 005", "TH04", 50),
        ("TH 006", "TH04", 50),
        ("Aha Khang", "TH04", 55),
        ("Dieu(Khang)", "TH04", 55),
        ("Duy Khang", "TH04", 50),
        ("Khang Ut 2", "TH04", 50),
        ("Ut Khang", "TH04", 60),
    ]

    all_data = th01_data + th02_data + th04_data

    with connect() as conn:
        cur = conn.cursor()
        for name, group_master, rate in all_data:
            cur.execute("""
                INSERT INTO weekly_info (name, group_master, rate)
                VALUES (%s, %s, %s)
                ON CONFLICT (name) DO UPDATE 
                SET group_master = EXCLUDED.group_master,
                    rate = EXCLUDED.rate
            """, (name, group_master, rate))
        conn.commit()
    print("✅ Done init DB (Auto Update)")
