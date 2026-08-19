import sqlite3
import joblib
import numpy as np
import tensorflow as tf

DB_PATH = '/Users/samarthbhatt/Desktop/db.sqlite3'

model = tf.keras.models.load_model('update_ready_model01large.keras')
scaler = joblib.load('scaler.pkl')
labels = {0: 'bump', 1: 'cruising', 2: 'rough road'}

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("""
    SELECT timestamp, ax_mg, ay_mg, az_mg, gx_dps, gy_dps, gz_dps
    FROM myapp_imurecord
    WHERE timestamp >= '2026-08-12 14:01:00'
      AND timestamp <= '2026-08-12 14:01:59'
    ORDER BY timestamp ASC
""")
rows = cursor.fetchall()
conn.close()

print(f"Total records: {len(rows)}")

data = np.array([[ax, ay, az, gx, gy, gz] for _, ax, ay, az, gx, gy, gz in rows])
data_scaled = scaler.transform(data)
predictions = model.predict(data_scaled)

for i, (row, pred) in enumerate(zip(rows, predictions)):
    predicted_class = int(np.argmax(pred))
    print(f"{row[0]} -> {labels[predicted_class]} ({[f'{p:.3f}' for p in pred]})")