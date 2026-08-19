import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DB_PATH = '/Users/samarthbhatt/Desktop/db.sqlite3'
REAL_DB = '/Users/samarthbhatt/Desktop/experiment.sqlite3'

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

last1_seconds = set()
for h, m, s_start, s_end in bump_windows:
    last1_seconds.add(f'2026-08-06 {h:02d}:{m:02d}:{s_end:02d}')

placeholders = ','.join(['?' for _ in last1_seconds])

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute(f"""
    SELECT ax_mg, ay_mg, az_mg, gx_dps, gy_dps, gz_dps
    FROM myapp_imurecord
    WHERE timestamp IN ({placeholders})
""", list(last1_seconds))
last1_rows = cursor.fetchall()
conn.close()

print(f"Last 1 second bump records found: {len(last1_rows)}")

conn2 = sqlite3.connect(REAL_DB)
cursor2 = conn2.cursor()
cursor2.execute("SELECT ax_mg, ay_mg, az_mg, gx_dps, gy_dps, gz_dps FROM imu_data")
cruise_rows = cursor2.fetchall()
conn2.close()

columns = ['ax_mg', 'ay_mg', 'az_mg', 'gx_dps', 'gy_dps', 'gz_dps']
last1_data = {col: [row[i] for row in last1_rows] for i, col in enumerate(columns)}
cruise_data = {col: [row[i] for row in cruise_rows] for i, col in enumerate(columns)}

for col in columns:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    ax1.hist(cruise_data[col], bins=50, color='steelblue', edgecolor='black')
    ax1.set_title(f'Cruising: {col}')
    ax1.set_xlabel('Value')
    ax1.set_ylabel('Frequency')

    ax2.hist(last1_data[col], bins=50, color='red', edgecolor='black')
    ax2.set_title(f'Last 1s of Bump: {col}')
    ax2.set_xlabel('Value')
    ax2.set_ylabel('Frequency')

    plt.tight_layout()
    plt.savefig(f'/Users/samarthbhatt/Desktop/{col}_last1s_vs_cruise.png')
    plt.close()
    print(f"Saved {col}_last1s_vs_cruise.png")

print("Done.")