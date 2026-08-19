import random
import csv
from datetime import datetime, timedelta

stats = {
    'ax_mg':  {'min': -10000, 'max': 10000},
    'ay_mg':  {'min': -10000, 'max': 10000},
    'az_mg':  {'min': -10000, 'max': 10000},
    'gx_dps': {'min': -300000, 'max': 300000},
    'gy_dps': {'min': -300000, 'max': 300000},
    'gz_dps': {'min': -300000, 'max': 300000},
}

def generate_bad_value(col):
    return random.randint(stats[col]['min'], stats[col]['max'])

NUM_RECORDS = 1_000_000
start_time = datetime(2026, 7, 15, 14, 50, 0) - timedelta(seconds=NUM_RECORDS)

CSV_PATH = '/Users/samarthbhatt/Desktop/bad_data.csv'
print("Generating and writing bad data records...")

with open(CSV_PATH, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['ax_mg', 'ay_mg', 'az_mg', 'gx_dps', 'gy_dps', 'gz_dps', 'label'])
    current = start_time
    for i in range(NUM_RECORDS):
        writer.writerow([
            current.strftime('%Y-%m-%d %H:%M:%S'),
            generate_bad_value('ax_mg'),
            generate_bad_value('ay_mg'),
            generate_bad_value('az_mg'),
            generate_bad_value('gx_dps'),
            generate_bad_value('gy_dps'),
            generate_bad_value('gz_dps'),
            0
        ])
        current += timedelta(seconds=1)
        if i % 100000 == 0:
            print(f"Progress: {i}/{NUM_RECORDS}")

print("Done.")