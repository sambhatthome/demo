import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DB_PATH = '/Users/samarthbhatt/Desktop/experiment.sqlite3'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT ax_mg, ay_mg, az_mg, gx_dps, gy_dps, gz_dps FROM imu_data")
rows = cursor.fetchall()
conn.close()

columns = ['ax_mg', 'ay_mg', 'az_mg', 'gx_dps', 'gy_dps', 'gz_dps']
data = {col: [row[i] for row in rows] for i, col in enumerate(columns)}

for col in columns:
    plt.figure(figsize=(8, 4))
    plt.hist(data[col], bins=50, color='steelblue', edgecolor='black')
    plt.title(f'Histogram of {col}')
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig(f'/Users/samarthbhatt/Desktop/{col}_histogram.png')
    plt.close()
    print(f"Saved {col}_histogram.png")

print("Done.")