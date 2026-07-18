import sqlite3
from datetime import datetime

SOURCE_DB = '/home/samarth/demo/db.sqlite3'
NEW_DB = '/home/samarth/demo/experiment.sqlite3'

# Read filtered data from source
conn = sqlite3.connect(SOURCE_DB)
cursor = conn.cursor()

cursor.execute("""
    SELECT id, timestamp, ax_mg, ay_mg, az_mg, gx_dps, gy_dps, gz_dps, activity
    FROM myapp_imurecord
    WHERE timestamp >= '2026-07-15 14:50:00'
      AND timestamp <= '2026-07-16 11:25:59'
      AND NOT (timestamp >= '2026-07-15 15:14:00' AND timestamp <= '2026-07-15 15:14:59')
      AND NOT (timestamp >= '2026-07-15 20:58:00' AND timestamp <= '2026-07-15 20:58:59')
    ORDER BY timestamp ASC
""")

rows = cursor.fetchall()
conn.close()

print(f"Total records after filtering: {len(rows)}")

# Write to new database
new_conn = sqlite3.connect(NEW_DB)
new_cursor = new_conn.cursor()

new_cursor.execute("""
    CREATE TABLE IF NOT EXISTS imu_data (
        id INTEGER PRIMARY KEY,
        timestamp TEXT,
        ax_mg INTEGER,
        ay_mg INTEGER,
        az_mg INTEGER,
        gx_dps INTEGER,
        gy_dps INTEGER,
        gz_dps INTEGER,
        activity TEXT
    )
""")

new_cursor.executemany("""
    INSERT INTO imu_data (id, timestamp, ax_mg, ay_mg, az_mg, gx_dps, gy_dps, gz_dps, activity)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", rows)

new_conn.commit()
new_conn.close()

print(f"Filtered data saved to {NEW_DB}")

# Detect laps
laps = []
if rows:
    lap_start = rows[0][1]
    prev_time = datetime.strptime(rows[0][1], '%Y-%m-%d %H:%M:%S')
    for row in rows[1:]:
        curr_time = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
        gap = (curr_time - prev_time).total_seconds()
        if gap > 4:
            laps.append((lap_start, prev_time.strftime('%Y-%m-%d %H:%M:%S')))
            lap_start = row[1]
        prev_time = curr_time
    laps.append((lap_start, rows[-1][1]))

print(f"\nTotal laps detected: {len(laps)}")
print("\nLap list:")
for i, (start, stop) in enumerate(laps, 1):
    print(f"Lap {i:3d}: {start}  →  {stop}")