import sqlite3
import numpy as np
import tensorflow as tf
import joblib

DB_PATH = '/Users/samarthbhatt/Desktop/db.sqlite3'

model = tf.keras.models.load_model('update_ready_model01large.keras')
scaler = joblib.load('scaler.pkl')
labels = {0: 'bump', 1: 'cruising', 2: 'rough road'}

cruise_ranges = {
    'ax_mg':  (-300, 300),
    'ay_mg':  (-200, 200),
    'az_mg':  (800, 1300),
    'gx_dps': (-13000, 17000),
    'gy_dps': (-12000, 13000),
    'gz_dps': (-22000, 17000),
}

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("""
    SELECT timestamp, ax_mg, ay_mg, az_mg, gx_dps, gy_dps, gz_dps
    FROM myapp_imurecord
    WHERE timestamp >= '2026-08-17 17:46:00'
      AND timestamp <= '2026-08-17 17:48:59'
    ORDER BY timestamp ASC
""")
rows = cursor.fetchall()
conn.close()

print(f"Total records: {len(rows)}")

cols = ['ax_mg', 'ay_mg', 'az_mg', 'gx_dps', 'gy_dps', 'gz_dps']

results = []
extreme_windows = []
extreme_indices = []

for i, row in enumerate(rows):
    _, ax, ay, az, gx, gy, gz = row
    values = [ax, ay, az, gx, gy, gz]
    is_extreme = any(abs(val) > abs(cruise_ranges[col][1]) for col, val in zip(cols, values))
    if is_extreme:
        start = max(0, i - 5)
        end = min(len(rows), i + 6)
        window = np.array([[r[1], r[2], r[3], r[4], r[5], r[6]] for r in rows[start:end]], dtype=np.float32)
        extreme_windows.append(scaler.transform(window))
        extreme_indices.append(i)
        results.append((row[0], None))
    else:
        results.append((row[0], 'cruising'))

if extreme_windows:
    max_len = max(len(w) for w in extreme_windows)
    X = tf.keras.preprocessing.sequence.pad_sequences(
        extreme_windows,
        maxlen=max_len,
        dtype='float32',
        padding='post',
        value=-1.0
    )
    predictions = model.predict(X)
    for idx, pred in zip(extreme_indices, predictions):
        predicted_class = int(np.argmax(pred))
        results[idx] = (results[idx][0], f"{labels[predicted_class]} ({[f'{p:.3f}' for p in pred]})")

# Post-processing: track consecutive extreme predictions
consecutive_extreme = 0
consecutive_normal = 0
final_results = []

for ts, label in results:
    if label is not None and ('bump' in label or 'rough road' in label):
        consecutive_extreme += 1
        consecutive_normal = 0
        if consecutive_extreme >= 4:
            final_results.append((ts, 'rough road (sustained)'))
        else:
            final_results.append((ts, label))
    else:
        consecutive_normal += 1
        if consecutive_normal >= 15:
            consecutive_extreme = 0
        final_results.append((ts, label))

for ts, label in final_results:
    print(f"{ts} -> {label}")