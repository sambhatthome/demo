import sqlite3
import csv

SYNTH_DB = '/Users/samarthbhatt/Desktop/synthetic.sqlite3'

print("Counting total records...")
conn = sqlite3.connect(SYNTH_DB)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM imu_data")
total = cursor.fetchone()[0]
print(f"Total records: {total}")

chunk_size = total // 4
print(f"Records per file: ~{chunk_size}")

cursor.execute("SELECT ax_mg, ay_mg, az_mg, gx_dps, gy_dps, gz_dps FROM imu_data ORDER BY timestamp ASC")

for part in range(1, 5):
    CSV_PATH = f'/Users/samarthbhatt/Desktop/synthetic_part{part}.csv'
    print(f"Writing {CSV_PATH}...")
    
    if part < 4:
        rows_to_write = chunk_size
    else:
        rows_to_write = total - (chunk_size * 3)
    
    with open(CSV_PATH, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ax_mg', 'ay_mg', 'az_mg', 'gx_dps', 'gy_dps', 'gz_dps'])
        written = 0
        while written < rows_to_write:
            batch = cursor.fetchmany(min(10000, rows_to_write - written))
            if not batch:
                break
            writer.writerows(batch)
            written += len(batch)

conn.close()
print("Done.")