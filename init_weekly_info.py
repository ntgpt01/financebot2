from db import connect  # hoặc from weekly_db import connect

def run_init():

    # === Bổ sung 2 Master ===
    master_data = [
        
        ("Master 05", "MASTER", 0),
        ("Master 03", "MASTER", 0),
    ]

    th01_data = [
        ("Atha", "TH01", 10),
        ("Bi", "TH01", 0),
        ("Thuy", "TH01", 0),
        ("Vk Gau", "TH01", 0),
        ("Tu", "TH01", 0),
        ("Lâm Bình", "TH01", 0),
        ("Vũ", "TH01", 25),
        ("Hieu", "TH01", 0),
        ("Huyền", "TH01", 0),
        ("Goem", "TH01", 0),
        ("Co Huong", "TH01", 0),
    ]

    th02_data = [
        ("Tuan(Vani)", "TH02", 30),
        ("Phung D", "TH02", 40),
        ("A6.3", "TH02", 40),
        ("A6.2", "TH02", 40),
        ("A6.usa", "TH02", 40),
        ("A6.4", "TH02", 20),
        ("ASang", "TH02", 20),
        ("CHang", "TH02", 35),
        ("ALiem", "TH02", 35),
        ("A6. A Tuan", "TH02", 30),
        ("Vinh", "TH02", 50),
        ("Family", "TH02", 35),
    ]

    th04_data = [
        ("Aha3 Khang", "TH04", 30),
        ("Ut Khang", "TH04", 60),
        ("Khang Ut 2", "TH04", 50),
        ("Duy Khang", "TH04", 50),
        ("Dieu(Khang)", "TH04", 55),
        ("Aha2 Khang", "TH04", 30),
        ("Aha Khang", "TH04", 45),
        ("TH 005", "TH04", 50),
        ("TH 004", "TH04", 50),
        ("TH 003", "TH04", 50),
        ("TH 002", "TH04", 50),
        ("TH 001", "TH04", 50),
        ("Trung", "TH04", 50),
        ("Khang", "TH04", 40),
    ]

    # === Master + TH04 + TH02 + TH01 ===
    all_data = master_data + th04_data + th02_data + th01_data

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
