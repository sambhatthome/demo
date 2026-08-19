import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DB_PATH = '/Users/samarthbhatt/Desktop/db.sqlite3'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("""
    SELECT ax_mg, ay_mg, az_mg, gx_dps, gy_dps, gz_dps
    FROM myapp_imurecord
    WHERE (timestamp >= '2026-08-11 16:40:00' AND timestamp <= '2026-08-11 17:00:59')
       OR (timestamp >= '2026-08-11 21:00:00' AND timestamp <= '2026-08-11 22:00:59')
""")
rough_rows = cursor.fetchall()
conn.close()

# Load bump data from August 6th using cruise ranges
cruise_ranges = {
    'ax_mg':  (-300, 300),
    'ay_mg':  (-200, 200),
    'az_mg':  (800, 1300),
    'gx_dps': (-13000, 17000),
    'gy_dps': (-12000, 13000),
    'gz_dps': (-22000, 17000),
}

bump_windows = [
    (17, 40, 8, 10), (17, 47, 6, 8), (17, 50, 7, 10), (17, 51, 32, 35),
    (17, 53, 5, 8), (17, 54, 6, 8), (17, 56, 7, 9), (18, 6, 8, 10),
    (18, 7, 5, 8), (18, 10, 6, 9), (18, 11, 8, 10), (18, 24, 5, 8),
    (18, 25, 6, 8), (18, 28, 7, 9), (18, 33, 5, 8), (18, 42, 6, 8),
    (18, 44, 6, 9), (18, 45, 8, 11), (18, 47, 5, 8), (18, 48, 5, 7),
    (18, 51, 9, 11), (18, 53, 6, 8), (18, 56, 9, 12), (18, 57, 8, 10),
    (18, 58, 8, 10), (18, 59, 17, 19), (19, 0, 8, 10), (19, 1, 40, 43),
    (19, 4, 7, 9), (19, 7, 6, 9),
]

minutes = [
    (17, 40), (17, 47), (17, 50), (17, 51), (17, 53), (17, 54), (17, 56),
    (18, 6), (18, 7), (18, 10), (18, 11), (18, 24), (18, 25), (18, 28),
    (18, 33), (18, 42), (18, 44), (18, 45), (18, 47), (18, 48), (18, 51),
    (18, 53), (18, 56), (18, 57), (18, 58), (18, 59),
    (19, 0), (19, 1), (19, 4), (19, 7)
]

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

bump_rows = []
for row in all_rows:
    timestamp, ax, ay, az, gx, gy, gz = row
    values = {'ax_mg': ax, 'ay_mg': ay, 'az_mg': az,
              'gx_dps': gx, 'gy_dps': gy, 'gz_dps': gz}
    if any(val < cruise_ranges[col][0] or val > cruise_ranges[col][1]
           for col, val in values.items()):
        bump_rows.append((ax, ay, az, gx, gy, gz))

columns = ['ax_mg', 'ay_mg', 'az_mg', 'gx_dps', 'gy_dps', 'gz_dps']
bump_data = {col: [row[i] for row in bump_rows] for i, col in enumerate(columns)}
rough_data = {col: [row[i] for row in rough_rows] for i, col in enumerate(columns)}

for col in columns:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    ax1.hist(bump_data[col], bins=50, color='red', edgecolor='black')
    ax1.set_title(f'Bump: {col}')
    ax1.set_xlabel('Value')
    ax1.set_ylabel('Frequency')

    ax2.hist(rough_data[col], bins=50, color='orange', edgecolor='black')
    ax2.set_title(f'Rough Road: {col}')
    ax2.set_xlabel('Value')
    ax2.set_ylabel('Frequency')

    plt.tight_layout()
    plt.savefig(f'/Users/samarthbhatt/Desktop/{col}_bump_vs_rough.png')
    plt.close()
    print(f"Saved {col}_bump_vs_rough.png")

print("Done.")