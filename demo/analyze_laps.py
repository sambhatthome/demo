import sqlite3
from datetime import datetime

DB_PATH = '/home/samarth/demo/db.sqlite3'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    SELECT timestamp
    FROM myapp_imurecord
    WHERE timestamp >= '2026-07-15T14:50:00Z'
      AND timestamp <= '2026-07-15T23:59:59Z'
      AND NOT (timestamp >= '2026-07-15T15:14:00Z' AND timestamp <= '2026-07-15T15:14:59Z')
      AND NOT (timestamp >= '2026-07-15T20:58:00Z' AND timestamp <= '2026-07-15T20:58:59Z')
    ORDER BY timestamp ASC
""")

rows = cursor.fetchall()
conn.close()

print(f"Total records: {len(rows)}")

lap_count = 0
if rows:
    prev_time = datetime.fromisoformat(rows[0][0].replace('Z', '+00:00'))
    lap_count = 1
    for row in rows[1:]:
        curr_time = datetime.fromisoformat(row[0].replace('Z', '+00:00'))
        if (curr_time - prev_time).total_seconds() > 2:
            lap_count += 1
        prev_time = curr_time

print(f"Total laps detected: {lap_count}")