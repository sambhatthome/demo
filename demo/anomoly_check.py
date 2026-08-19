import sqlite3

DB_PATH = '/Users/samarthbhatt/Desktop/db.sqlite3'

bump_windows = [
    (17, 40, 8, 10),
    (17, 47, 6, 8),
    (17, 50, 7, 10),
    (17, 51, 32, 35),
    (17, 53, 5, 8),
    (17, 54, 6, 8),
    (17, 56, 7, 9),
    (18, 6, 8, 10),
    (18, 7, 5, 8),
    (18, 10, 6, 9),
    (18, 11, 8, 10),
    (18, 24, 5, 8),
    (18, 25, 6, 8),
    (18, 28, 7, 9),
    (18, 33, 5, 8),
    (18, 42, 6, 8),
    (18, 44, 6, 9),
    (18, 45, 8, 11),
    (18, 47, 5, 8),
    (18, 48, 5, 7),
    (18, 51, 9, 11),
    (18, 53, 6, 8),
    (18, 56, 9, 12),
    (18, 57, 8, 10),
    (18, 58, 8, 10),
    (18, 59, 17, 19),
    (19, 0, 8, 10),
    (19, 1, 40, 43),
    (19, 4, 7, 9),
    (19, 7, 6, 9),
]

minutes = [
    (17, 40), (17, 47), (17, 50), (17, 51), (17, 53), (17, 54), (17, 56),
    (18, 6), (18, 7), (18, 10), (18, 11), (18, 24), (18, 25), (18, 28),
    (18, 33), (18, 42), (18, 44), (18, 45), (18, 47), (18, 48), (18, 51),
    (18, 53), (18, 56), (18, 57), (18, 58), (18, 59),
    (19, 0), (19, 1), (19, 4), (19, 7)
]

cruise_ranges = {
    'ax_mg':  (-21, 183),
    'ay_mg':  (-68, 146),
    'az_mg':  (953, 1097),
    'gx_dps': (-6413, 8863),
    'gy_dps': (-4392, 6501),
    'gz_dps': (-13868, 9668),
}

bump_seconds = set()
for h, m, s_start, s_end in bump_windows:
    for s in range(s_start, s_end + 1):
        bump_seconds.add(f'2026-08-06 {h:02d}:{m:02d}:{s:02d}')

minute_filters = ' OR '.join([
    f"(timestamp >= '2026-08-06 {h:02d}:{m:02d}:00' AND timestamp <= '2026-08-06 {h:02d}:{m:02d}:59')"
    for h, m in minutes
])

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute(f"""
    SELECT timestamp, ax_mg, ay_mg, az_mg, gx_dps, gy_dps, gz_dps
    FROM myapp_imurecord
    WHERE {minute_filters}
    ORDER BY timestamp ASC
""")
all_rows = cursor.fetchall()
conn.close()

outside_seconds = set()
for row in all_rows:
    timestamp, ax, ay, az, gx, gy, gz = row
    ts_second = timestamp[:19]

    if ts_second in bump_seconds:
        continue

    values = {
        'ax_mg': ax, 'ay_mg': ay, 'az_mg': az,
        'gx_dps': gx, 'gy_dps': gy, 'gz_dps': gz
    }

    for col, val in values.items():
        lo, hi = cruise_ranges[col]
        if val < lo or val > hi:
            outside_seconds.add(ts_second)
            break

for ts in sorted(outside_seconds):
    print(ts)

print(f"\nTotal unique seconds outside cruising range but not in bump seconds: {len(outside_seconds)}")