import sqlite3

DB_PATH = '/Users/samarthbhatt/Desktop/db.sqlite3'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("""
    SELECT 
        MIN(ax_mg), MAX(ax_mg),
        MIN(ay_mg), MAX(ay_mg),
        MIN(az_mg), MAX(az_mg),
        MIN(gx_dps), MAX(gx_dps),
        MIN(gy_dps), MAX(gy_dps),
        MIN(gz_dps), MAX(gz_dps)
    FROM myapp_imurecord
    WHERE timestamp >= '2026-08-10 22:07:00'
      AND timestamp <= '2026-08-10 22:15:59'
""")
row = cursor.fetchone()
conn.close()

cols = ['ax_mg', 'ay_mg', 'az_mg', 'gx_dps', 'gy_dps', 'gz_dps']
for i, col in enumerate(cols):
    print(f"{col}: min={row[i*2]}, max={row[i*2+1]}")