import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DB_PATH = '/Users/samarthbhatt/Desktop/db.sqlite3'
REAL_DB = '/Users/samarthbhatt/Desktop/experiment.sqlite3'

bump_seconds = []

def add_bump(hour, minute, sec_start, sec_end):
    for s in range(sec_start, sec_end + 1):
        bump_seconds.append(f'2026-08-06 {hour:02d}:{minute:02d}:{s:02d}')

add_bump(17, 40, 8, 10)
add_bump(17, 47, 6, 8)
add_bump(17, 50, 7, 10)
add_bump(17, 51, 32, 35)
add_bump(17, 53, 5, 8)
add_bump(17, 54, 6, 8)
add_bump(17, 56, 7, 9)
add_bump(18, 6, 8, 10)
add_bump(18, 7, 5, 8)
add_bump(18, 10, 6, 9)
add_bump(18, 11, 8, 10)
add_bump(18, 24, 5, 8)
add_bump(18, 25, 6, 8)
add_bump(18, 28, 7, 9)
add_bump(18, 33, 5, 8)
add_bump(18, 42, 6, 8)
add_bump(18, 44, 6, 9)
add_bump(18, 45, 8, 11)
add_bump(18, 47, 5, 8)
add_bump(18, 48, 5, 7)
add_bump(18, 51, 9, 11)
add_bump(18, 53, 6, 8)
add_bump(18, 56, 9, 12)
add_bump(18, 57, 8, 10)
add_bump(18, 58, 8, 10)
add_bump(18, 59, 17, 19)
add_bump(19, 0, 8, 10)
add_bump(19, 1, 40, 43)
add_bump(19, 4, 7, 9)
add_bump(19, 7, 6, 9)

placeholders = ','.join(['?' for _ in bump_seconds])

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute(f"""
    SELECT ax_mg, ay_mg, az_mg, gx_dps, gy_dps, gz_dps
    FROM myapp_imurecord
    WHERE timestamp IN ({placeholders})
""", bump_seconds)
bump_rows = cursor.fetchall()
conn.close()

print(f"Bump records found: {len(bump_rows)}")

conn2 = sqlite3.connect(REAL_DB)
cursor2 = conn2.cursor()
cursor2.execute("SELECT ax_mg, ay_mg, az_mg, gx_dps, gy_dps, gz_dps FROM imu_data")
cruise_rows = cursor2.fetchall()
conn2.close()

columns = ['ax_mg', 'ay_mg', 'az_mg', 'gx_dps', 'gy_dps', 'gz_dps']
bump_data = {col: [row[i] for row in bump_rows] for i, col in enumerate(columns)}
cruise_data = {col: [row[i] for row in cruise_rows] for i, col in enumerate(columns)}

for col in columns:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    ax1.hist(cruise_data[col], bins=50, color='steelblue', edgecolor='black')
    ax1.set_title(f'Cruising: {col}')
    ax1.set_xlabel('Value')
    ax1.set_ylabel('Frequency')

    ax2.hist(bump_data[col], bins=50, color='red', edgecolor='black')
    ax2.set_title(f'Bump: {col}')
    ax2.set_xlabel('Value')
    ax2.set_ylabel('Frequency')

    plt.tight_layout()
    plt.savefig(f'/Users/samarthbhatt/Desktop/{col}_bump_vs_cruise.png')
    plt.close()
    print(f"Saved {col}_bump_vs_cruise.png")

print("Done.")