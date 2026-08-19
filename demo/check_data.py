import sqlite3

DB_PATH = '/Users/samarthbhatt/Desktop/db.sqlite3'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("""
    SELECT timestamp, COUNT(*) as count
    FROM myapp_imurecord
    WHERE timestamp >= '2026-08-06 17:40:08'
      AND timestamp <= '2026-08-06 17:40:12'
    GROUP BY timestamp
    ORDER BY timestamp ASC
""")
rows = cursor.fetchall()
conn.close()

for row in rows:
    print(row)

import sqlite3

DB_PATH = '/Users/samarthbhatt/Desktop/db.sqlite3'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("""
    SELECT timestamp, ax_mg, ay_mg, az_mg, gx_dps, gy_dps, gz_dps
    FROM myapp_imurecord
    WHERE timestamp >= '2026-08-06 17:40:07'
      AND timestamp <= '2026-08-06 17:40:11'
    ORDER BY timestamp ASC
""")
rows = cursor.fetchall()
conn.close()

for row in rows:
    print(row)

cruise_ranges = {
    'ax_mg':  (-300, 300),
    'ay_mg':  (-200, 200),
    'az_mg':  (800, 1300),
    'gx_dps': (-13000, 17000),
    'gy_dps': (-12000, 13000),
    'gz_dps': (-22000, 17000),
}

for row in rows:
    _, ax, ay, az, gx, gy, gz = row
    values = {'ax_mg': ax, 'ay_mg': ay, 'az_mg': az,
              'gx_dps': gx, 'gy_dps': gy, 'gz_dps': gz}
    is_extreme = any(
        abs(val) > abs(cruise_ranges[col][1]) * 3
        for col, val in values.items()
    )
    if is_extreme:
        print(f"EXTREME: {row}")

    conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("""
    SELECT timestamp, ax_mg, ay_mg, az_mg, gx_dps, gy_dps, gz_dps
    FROM myapp_imurecord
    WHERE timestamp >= '2026-08-12 12:04:00'
      AND timestamp <= '2026-08-12 12:04:59'
    ORDER BY timestamp ASC
""")
aug12_rows = cursor.fetchall()
conn.close()

print(f"\nAugust 12th bump records: {len(aug12_rows)}")
for row in aug12_rows:
    _, ax, ay, az, gx, gy, gz = row
    values = {'ax_mg': ax, 'ay_mg': ay, 'az_mg': az,
              'gx_dps': gx, 'gy_dps': gy, 'gz_dps': gz}
    is_extreme = any(
        abs(val) > abs(cruise_ranges[col][1]) * 1
        for col, val in values.items()
    )
    if is_extreme:
        print(f"EXTREME: {row}")