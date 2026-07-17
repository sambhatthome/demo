import sqlite3
from datetime import datetime

DB_PATH = '/home/samarth/demo/db.sqlite3'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    SELECT timestamp
    FROM myapp_imurecord
    WHERE timestamp >= '2026-07-15 14:50:00'
      AND timestamp <= '2026-07-15 23:59:59'
      AND NOT (timestamp >= '2026-07-15 15:14:00' AND timestamp <= '2026-07-15 15:14:59')
      AND NOT (timestamp >= '2026-07-15 20:58:00' AND timestamp <= '2026-07-15 20:58:59')
    ORDER BY timestamp ASC
""")

rows = cursor.fetchall()
conn.close()

print(f"Total records: {len(rows)}")

lap_count = 0
if rows:
    prev_time = datetime.strptime(rows[0][0], '%Y-%m-%d %H:%M:%S')
    lap_count = 1
    for row in rows[1:]:
        curr_time = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
        if (curr_time - prev_time).total_seconds() > 2:
            lap_count += 1
        prev_time = curr_time

print(f"Total laps detected: {lap_count}")