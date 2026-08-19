import sqlite3
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
import joblib
import numpy as np

DB_PATH = '/Users/samarthbhatt/Desktop/db.sqlite3'
SYNTH_PATH = '/Users/samarthbhatt/Desktop/synthetic.csv'

# Cruising ranges
cruise_ranges = {
    'ax_mg':  (-300, 300),
    'ay_mg':  (-200, 200),
    'az_mg':  (800, 1300),
    'gx_dps': (-13000, 17000),
    'gy_dps': (-12000, 13000),
    'gz_dps': (-22000, 17000),
}

minutes = [
    (17, 40), (17, 47), (17, 50), (17, 51), (17, 53), (17, 54), (17, 56),
    (18, 6), (18, 7), (18, 10), (18, 11), (18, 24), (18, 25), (18, 28),
    (18, 33), (18, 42), (18, 44), (18, 45), (18, 47), (18, 48), (18, 51),
    (18, 53), (18, 56), (18, 57), (18, 58), (18, 59),
    (19, 0), (19, 1), (19, 4), (19, 7)
]

minute_filters = ' OR '.join([
    f"(timestamp >= '2026-08-06 {h:02d}:{m:02d}:00' AND timestamp <= '2026-08-06 {h:02d}:{m:02d}:59')"
    for h, m in minutes
])

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute(f"""
    SELECT timestamp, ax_mg, ay_mg, az_mg, gx_dps, gy_dps, gz_dps
    FROM myapp_imurecord
    WHERE {minute_filters}
    ORDER BY timestamp ASC
""")
rows = cursor.fetchall()
conn.close()

print(f"Total August 6th records from those minutes: {len(rows)}")

bump_records = []
cruise_records = []

for row in rows:
    timestamp, ax, ay, az, gx, gy, gz = row
    values = {
        'ax_mg': ax, 'ay_mg': ay, 'az_mg': az,
        'gx_dps': gx, 'gy_dps': gy, 'gz_dps': gz
    }
    is_bump = False
    for col, val in values.items():
        lo, hi = cruise_ranges[col]
        if val < lo or val > hi:
            is_bump = True
            break
    if is_bump:
        bump_records.append([ax, ay, az, gx, gy, gz, 0])
    else:
        cruise_records.append([ax, ay, az, gx, gy, gz, 1])

print(f"Bump records: {len(bump_records)}")
print(f"Cruise records from August 6th: {len(cruise_records)}")

print("Loading synthetic cruising data...")
synth_df = pd.read_csv(SYNTH_PATH)
synth_df['label'] = 1
synth_df = synth_df.sample(n=903, random_state=42).reset_index(drop=True)

bump_df = pd.DataFrame(bump_records, columns=['ax_mg', 'ay_mg', 'az_mg', 'gx_dps', 'gy_dps', 'gz_dps', 'label'])
cruise_aug6_df = pd.DataFrame(cruise_records, columns=['ax_mg', 'ay_mg', 'az_mg', 'gx_dps', 'gy_dps', 'gz_dps', 'label'])

df = pd.concat([synth_df, cruise_aug6_df, bump_df], ignore_index=True)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

X = df[['ax_mg', 'ay_mg', 'az_mg', 'gx_dps', 'gy_dps', 'gz_dps']].values
y = df['label'].values

print(f"Total training records: {len(df)}")
print(f"Total bump records: {len(bump_df)}")
print(f"Total cruising records: {len(df) - len(bump_df)}")

print("Normalizing...")
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)
joblib.dump(scaler, 'scaler.pkl')
print("Scaler saved.")

model = keras.Sequential([
    keras.layers.Input(shape=(6,)),
    keras.layers.Dense(32, activation='relu'),
    keras.layers.Dense(16, activation='relu'),
    keras.layers.Dense(8, activation='relu'),
    keras.layers.Dense(1, activation='sigmoid')
])

print("1")
model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])
print("2")
model.fit(X_scaled, y, epochs=30, batch_size=16, validation_split=0.2)
model.save("update_ready_model01large.keras")

try:
    model.save("update_ready_model1.h5")
except:
    pass