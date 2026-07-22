import sqlite3
import statistics

DB_PATH = '/Users/samarthbhatt/Desktop/experiment.sqlite3'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT ax_mg, ay_mg, az_mg, gx_dps, gy_dps, gz_dps FROM imu_data")
rows = cursor.fetchall()
conn.close()

columns = ['ax_mg', 'ay_mg', 'az_mg', 'gx_dps', 'gy_dps', 'gz_dps']
data = {col: [row[i] for row in rows] for i, col in enumerate(columns)}

for col in columns:
    values = data[col]
    print(f"{col}:")
    print(f"  Mean:   {statistics.mean(values):.2f}")
    print(f"  StdDev: {statistics.stdev(values):.2f}")
    print(f"  Min:    {min(values)}")
    print(f"  Max:    {max(values)}")
    print()