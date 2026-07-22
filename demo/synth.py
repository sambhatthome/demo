import sqlite3
import statistics
import random
from datetime import datetime, timedelta

DB_PATH = '/Users/samarthbhatt/Desktop/experiment.sqlite3'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT ax_mg, ay_mg, az_mg, gx_dps, gy_dps, gz_dps FROM imu_data")
rows = cursor.fetchall()
conn.close()

columns = ['ax_mg', 'ay_mg', 'az_mg', 'gx_dps', 'gy_dps', 'gz_dps']
data = {col: [row[i] for row in rows] for i, col in enumerate(columns)}

stats = {}
for col in columns:
    values = data[col]
    mean = statistics.mean(values)
    std = statistics.stdev(values)
    stats[col] = {
        'mean': mean,
        'std': std,
        'min': min(values),
        'max': max(values)
    }

def generate_value(col):
    mean = stats[col]['mean']
    std = stats[col]['std']
    min_val = stats[col]['min']
    max_val = stats[col]['max']
    value = round(random.gauss(mean, std))
    value = max(min_val, min(max_val, value))
    return value

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT timestamp FROM imu_data ORDER BY timestamp ASC")
timestamp_rows = cursor.fetchall()
conn.close()

# Get first and last timestamps from real data
first_timestamp = datetime.strptime(timestamp_rows[0][0], '%Y-%m-%d %H:%M:%S')
last_timestamp = datetime.strptime(timestamp_rows[-1][0], '%Y-%m-%d %H:%M:%S')

# Detect gaps between laps
gaps = []
prev_time = first_timestamp
for row in timestamp_rows[1:]:
    curr_time = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
    gap = (curr_time - prev_time).total_seconds()
    if gap > 4:
        gaps.append((prev_time, curr_time))
    prev_time = curr_time

print(f"Gaps found: {len(gaps)}")

# Generate gap synthetic records
gap_records = []
for gap_start, gap_end in gaps:
    current = gap_start + timedelta(seconds=1)
    while current < gap_end:
        timestamp_str = current.strftime('%Y-%m-%d %H:%M:%S')
        gap_records.append((
            timestamp_str,
            generate_value('ax_mg'),
            generate_value('ay_mg'),
            generate_value('az_mg'),
            generate_value('gx_dps'),
            generate_value('gy_dps'),
            generate_value('gz_dps'),
            'Driving'
        ))
        current += timedelta(seconds=1)

print(f"Gap synthetic records generated: {len(gap_records)}")

# Get real records
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT timestamp, ax_mg, ay_mg, az_mg, gx_dps, gy_dps, gz_dps, activity FROM imu_data ORDER BY timestamp ASC")
real_records = cursor.fetchall()
conn.close()

real_count = len(real_records)
gap_count = len(gap_records)
target = 10_000_000
pre_count = target - real_count - gap_count

print(f"Real records: {real_count}")
print(f"Pre-data synthetic records needed: {pre_count}")

# Generate pre-data synthetic records counting backwards from first timestamp
pre_records = []
current = first_timestamp - timedelta(seconds=1)
for _ in range(pre_count):
    timestamp_str = current.strftime('%Y-%m-%d %H:%M:%S')
    pre_records.append((
        timestamp_str,
        generate_value('ax_mg'),
        generate_value('ay_mg'),
        generate_value('az_mg'),
        generate_value('gx_dps'),
        generate_value('gy_dps'),
        generate_value('gz_dps'),
        'Driving'
    ))
    current -= timedelta(seconds=1)

print(f"Pre-data synthetic records generated: {len(pre_records)}")

# Reverse so timestamps go forward in time
pre_records.reverse()

# Write everything to synthetic.sqlite3
SYNTH_DB = '/Users/samarthbhatt/Desktop/synthetic.sqlite3'
synth_conn = sqlite3.connect(SYNTH_DB)
synth_cursor = synth_conn.cursor()

synth_cursor.execute("DROP TABLE IF EXISTS imu_data")
synth_cursor.execute("""
    CREATE TABLE imu_data (
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

print("Inserting pre-data synthetic records...")
synth_cursor.executemany("""
    INSERT INTO imu_data (timestamp, ax_mg, ay_mg, az_mg, gx_dps, gy_dps, gz_dps, activity)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", pre_records)

print("Inserting real records and gap synthetic records...")
all_middle = sorted(list(real_records) + gap_records, key=lambda x: x[0])
synth_cursor.executemany("""
    INSERT INTO imu_data (timestamp, ax_mg, ay_mg, az_mg, gx_dps, gy_dps, gz_dps, activity)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", all_middle)

synth_conn.commit()
synth_conn.close()

total = pre_count + real_count + gap_count
print(f"\nTotal records in synthetic.sqlite3: {total}")
print("Done.")