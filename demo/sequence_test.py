import sqlite3

DB_PATH = '/Users/samarthbhatt/Desktop/db.sqlite3'

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

def is_outside(ax, ay, az, gx, gy, gz):
    values = {'ax_mg': ax, 'ay_mg': ay, 'az_mg': az,
              'gx_dps': gx, 'gy_dps': gy, 'gz_dps': gz}
    return any(val < cruise_ranges[col][0] or val > cruise_ranges[col][1]
               for col, val in values.items())

sequences = []
current_seq = []

for row in rows:
    timestamp, ax, ay, az, gx, gy, gz = row
    if is_outside(ax, ay, az, gx, gy, gz):
        current_seq.append(row)
    else:
        if len(current_seq) >= 3:
            sequences.append(current_seq)
        current_seq = []

if len(current_seq) >= 3:
    sequences.append(current_seq)

print(f"Sequences of 3+ consecutive outside-range records: {len(sequences)}")
print()
for i, seq in enumerate(sequences, 1):
    timestamps = sorted(set(row[0][:19] for row in seq))
    print(f"Sequence {i:2d} (length {len(seq):3d}): {timestamps[0]} to {timestamps[-1]}")

# Find 2-record sequences in 18:58
print("\n2-record sequences in 18:58:")
current_seq = []
two_record_seqs = []

for row in rows:
    timestamp, ax, ay, az, gx, gy, gz = row
    if '2026-08-06 18:58' not in timestamp:
        if len(current_seq) == 2:
            two_record_seqs.append(current_seq)
        if len(current_seq) > 0:
            current_seq = []
        continue
    if is_outside(ax, ay, az, gx, gy, gz):
        current_seq.append(row)
    else:
        if len(current_seq) == 2:
            two_record_seqs.append(current_seq)
        current_seq = []

for seq in two_record_seqs:
    for row in seq:
        print(row)
    print()