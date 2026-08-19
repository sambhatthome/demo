import sqlite3
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.optimizers import Adam
import joblib
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import random

DB_PATH = '/Users/samarthbhatt/Desktop/db.sqlite3'
EXPERIMENT_DB = '/Users/samarthbhatt/Desktop/experiment.sqlite3'
SYNTH_PATH = '/Users/samarthbhatt/Desktop/synthetic.csv'

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
aug6_rows = cursor.fetchall()

cursor.execute("""
    SELECT timestamp, ax_mg, ay_mg, az_mg, gx_dps, gy_dps, gz_dps
    FROM myapp_imurecord
    WHERE (timestamp >= '2026-08-11 16:40:00' AND timestamp <= '2026-08-11 17:00:59')
       OR (timestamp >= '2026-08-11 21:00:00' AND timestamp <= '2026-08-11 22:00:59')
    ORDER BY timestamp ASC
""")
rough_rows = cursor.fetchall()

cursor.execute("""
    SELECT timestamp, ax_mg, ay_mg, az_mg, gx_dps, gy_dps, gz_dps
    FROM myapp_imurecord
    WHERE timestamp >= '2026-08-10 22:07:00'
      AND timestamp <= '2026-08-10 22:15:59'
    ORDER BY timestamp ASC
""")
aug10_rows = cursor.fetchall()

cursor.execute("""
    SELECT timestamp, ax_mg, ay_mg, az_mg, gx_dps, gy_dps, gz_dps
    FROM myapp_imurecord
    WHERE timestamp >= '2026-08-12 12:04:00'
      AND timestamp <= '2026-08-12 12:04:59'
    ORDER BY timestamp ASC
""")
aug12_bump_rows = cursor.fetchall()

cursor.execute("""
    SELECT timestamp, ax_mg, ay_mg, az_mg, gx_dps, gy_dps, gz_dps
    FROM myapp_imurecord
    WHERE timestamp >= '2026-08-12 12:05:00'
      AND timestamp <= '2026-08-12 12:05:59'
    ORDER BY timestamp ASC
""")
aug12_rough_rows = cursor.fetchall()
conn.close()

conn2 = sqlite3.connect(EXPERIMENT_DB)
cursor2 = conn2.cursor()
cursor2.execute("SELECT timestamp, ax_mg, ay_mg, az_mg, gx_dps, gy_dps, gz_dps FROM imu_data ORDER BY timestamp ASC")
experiment_rows = cursor2.fetchall()
conn2.close()

print("Loading synthetic data...")
synth_df = pd.read_csv(SYNTH_PATH)
synth_df = synth_df.sample(n=10000, random_state=42).reset_index(drop=True)
synth_rows = [('synthetic', row['ax_mg'], row['ay_mg'], row['az_mg'],
               row['gx_dps'], row['gy_dps'], row['gz_dps'])
              for _, row in synth_df.iterrows()]

def is_outside(row):
    _, ax, ay, az, gx, gy, gz = row
    values = {'ax_mg': ax, 'ay_mg': ay, 'az_mg': az,
              'gx_dps': gx, 'gy_dps': gy, 'gz_dps': gz}
    return any(val < cruise_ranges[col][0] or val > cruise_ranges[col][1]
               for col, val in values.items())

def extract_outside_sequences(rows, min_length, label, context=2):
    sequences = []
    i = 0
    while i < len(rows):
        if is_outside(rows[i]):
            seq = []
            start = max(0, i - context)
            for j in range(start, i):
                if not is_outside(rows[j]):
                    seq.append(list(rows[j][1:]))
            while i < len(rows) and is_outside(rows[i]):
                seq.append(list(rows[i][1:]))
                i += 1
            end = min(len(rows), i + context)
            for j in range(i, end):
                if not is_outside(rows[j]):
                    seq.append(list(rows[j][1:]))
            if sum(1 for j in range(len(seq)) if j >= context and j < len(seq) - context) >= min_length:
                sequences.append((np.array(seq, dtype=np.float32), label))
        else:
            i += 1
    return sequences

def extract_extreme_sequences(rows, label, threshold_multiplier=5, context=5):
    sequences = []
    i = 0
    while i < len(rows):
        _, ax, ay, az, gx, gy, gz = rows[i]
        values = {'ax_mg': ax, 'ay_mg': ay, 'az_mg': az,
                  'gx_dps': gx, 'gy_dps': gy, 'gz_dps': gz}
        is_extreme = any(
            abs(val) > abs(cruise_ranges[col][1]) * threshold_multiplier
            for col, val in values.items()
        )
        if is_extreme:
            j = i
            while j < len(rows):
                _, ax2, ay2, az2, gx2, gy2, gz2 = rows[j]
                vals2 = {'ax_mg': ax2, 'ay_mg': ay2, 'az_mg': az2,
                         'gx_dps': gx2, 'gy_dps': gy2, 'gz_dps': gz2}
                if any(abs(v) > abs(cruise_ranges[col][1]) * threshold_multiplier
                       for col, v in vals2.items()):
                    j += 1
                else:
                    break
            start = max(0, i - context)
            end = min(len(rows), j + context)
            seq = [list(rows[k][1:]) for k in range(start, end)]
            sequences.append((np.array(seq, dtype=np.float32), label))
            i = j
        else:
            i += 1
    return sequences

def augment_sequences(sequences, n_augments=5, noise_factor=0.05):
    augmented = []
    for seq, label in sequences:
        augmented.append((seq, label))
        for _ in range(n_augments):
            noise = np.random.normal(0, noise_factor, seq.shape).astype(np.float32)
            augmented.append((seq + noise, label))
    return augmented

def extract_inside_sequences(rows, min_length, label):
    sequences = []
    current_seq = []
    for row in rows:
        if not is_outside(row):
            current_seq.append(list(row[1:]))
        else:
            if len(current_seq) >= min_length:
                sequences.append((np.array(current_seq, dtype=np.float32), label))
            current_seq = []
    if len(current_seq) >= min_length:
        sequences.append((np.array(current_seq, dtype=np.float32), label))
    return sequences

def chunk_sequences(sequences, chunk_size):
    chunked = []
    for seq, label in sequences:
        for i in range(0, len(seq), chunk_size):
            chunk = seq[i:i+chunk_size]
            if len(chunk) >= 3:
                chunked.append((chunk, label))
    return chunked

# Extract bump sequences
bump_seqs = extract_outside_sequences(aug6_rows, 2, 0, context=5)
bump_seqs = augment_sequences(bump_seqs, n_augments=5)
bump_seqs += extract_extreme_sequences(aug6_rows, 0, threshold_multiplier=3, context=5)

# Add August 12th bump sequences
aug12_bump_seqs = extract_extreme_sequences(aug12_bump_rows, 0, threshold_multiplier=1, context=5)
print(f"Aug12 bump sequences added: {len(aug12_bump_seqs)}")
bump_seqs += aug12_bump_seqs

# Deduplicate bump sequences
seen = set()
deduped_bump_seqs = []
for seq, label in bump_seqs:
    key = tuple(seq.flatten().round(2))
    if key not in seen:
        seen.add(key)
        deduped_bump_seqs.append((seq, label))
bump_seqs = deduped_bump_seqs

# Extract cruising sequences
cruise_seqs = extract_inside_sequences(aug6_rows, 3, 1)
cruise_seqs += extract_inside_sequences(aug10_rows, 3, 1)
cruise_seqs += extract_inside_sequences(experiment_rows, 3, 1)
cruise_seqs += extract_inside_sequences(synth_rows, 3, 1)
cruise_seqs = chunk_sequences(cruise_seqs, 10)

# Extract rough road sequences
rough_seqs = extract_outside_sequences(rough_rows, 3, 2, context=0)
rough_seqs += extract_outside_sequences(aug12_rough_rows, 3, 2, context=0)
rough_seqs = chunk_sequences(rough_seqs, 10)

bump_lengths = [len(seq) for seq, _ in bump_seqs]
cruise_lengths = [len(seq) for seq, _ in cruise_seqs]
rough_lengths = [len(seq) for seq, _ in rough_seqs]
print(f"Bump lengths: min={min(bump_lengths)}, max={max(bump_lengths)}, avg={sum(bump_lengths)/len(bump_lengths):.1f}")
print(f"Cruise lengths: min={min(cruise_lengths)}, max={max(cruise_lengths)}, avg={sum(cruise_lengths)/len(cruise_lengths):.1f}")
print(f"Rough lengths: min={min(rough_lengths)}, max={max(rough_lengths)}, avg={sum(rough_lengths)/len(rough_lengths):.1f}")
print(f"Bump sequences: {len(bump_seqs)}")
print(f"Cruising sequences: {len(cruise_seqs)}")
print(f"Rough road sequences: {len(rough_seqs)}")

# Balance and combine
n_target = len(bump_seqs) + len(rough_seqs)
cruise_sampled = random.sample(cruise_seqs, min(n_target, len(cruise_seqs)))
all_seqs = bump_seqs + cruise_sampled + rough_seqs
np.random.shuffle(all_seqs)

# Normalize
all_values = np.concatenate([seq for seq, _ in all_seqs], axis=0)
scaler = MinMaxScaler()
scaler.fit(all_values)
joblib.dump(scaler, 'scaler.pkl')
print("Scaler saved.")

# Scale sequences
scaled_seqs = [(scaler.transform(seq), label) for seq, label in all_seqs]
y = np.array([label for _, label in scaled_seqs])
print(f"Total sequences: {len(scaled_seqs)}")

# Pad sequences
max_len = max(len(seq) for seq, _ in scaled_seqs)
print(f"Max sequence length: {max_len}")

X = tf.keras.preprocessing.sequence.pad_sequences(
    [seq for seq, _ in scaled_seqs],
    maxlen=max_len,
    dtype='float32',
    padding='post',
    value=-1.0
)
print(f"X shape: {X.shape}")

# Build model
model = keras.Sequential([
    keras.layers.Input(shape=(max_len, 6)),
    keras.layers.Masking(mask_value=-1.0),
    keras.layers.LSTM(64, return_sequences=True),
    keras.layers.LSTM(32),
    keras.layers.Dense(16, activation='relu'),
    keras.layers.Dense(3, activation='softmax')
])

model.summary()
model.compile(optimizer=Adam(learning_rate=0.001),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
model.fit(X, y, epochs=30, batch_size=16, validation_split=0.2)
model.save("update_ready_model01large.keras")

try:
    model.save("update_ready_model1.h5")
except:
    pass