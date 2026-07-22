import sqlite3
import matplotlib.pyplot as plt

SYNTH_DB = '/Users/samarthbhatt/Desktop/synthetic.sqlite3'
REAL_DB = '/Users/samarthbhatt/Desktop/experiment.sqlite3'

def get_data(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT ax_mg, ay_mg, az_mg, gx_dps, gy_dps, gz_dps FROM imu_data")
    rows = cursor.fetchall()
    conn.close()
    return rows

real_rows = get_data(REAL_DB)
synth_rows = get_data(SYNTH_DB)

columns = ['ax_mg', 'ay_mg', 'az_mg', 'gx_dps', 'gy_dps', 'gz_dps']

real_data = {col: [row[i] for row in real_rows] for i, col in enumerate(columns)}
synth_data = {col: [row[i] for row in synth_rows] for i, col in enumerate(columns)}

for col in columns:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    ax1.hist(real_data[col], bins=50, color='steelblue', edgecolor='black')
    ax1.set_title(f'Real: {col}')
    ax1.set_xlabel('Value')
    ax1.set_ylabel('Frequency')
    
    ax2.hist(synth_data[col], bins=50, color='orange', edgecolor='black')
    ax2.set_title(f'Synthetic: {col}')
    ax2.set_xlabel('Value')
    ax2.set_ylabel('Frequency')
    
    plt.tight_layout()
    plt.savefig(f'/Users/samarthbhatt/Desktop/{col}_comparison.png')
    plt.close()
    print(f"Saved {col}_comparison.png")

print("Done.")