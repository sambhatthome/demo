import tensorflow as tf
from tensorflow import keras
import numpy as np
import pandas as pd
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
import joblib

print("Loading good data (sampling 1 million)...")
good_df = pd.read_csv('/Users/samarthbhatt/Desktop/synthetic.csv')
good_df['label'] = 1
good_df = good_df.sample(n=1_000_000, random_state=42).reset_index(drop=True)

print("Loading bad data...")
bad_df = pd.read_csv('/Users/samarthbhatt/Desktop/bad_data.csv')

print("Combining datasets...")
df = pd.concat([good_df, bad_df], ignore_index=True)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

X = df[['ax_mg', 'ay_mg', 'az_mg', 'gx_dps', 'gy_dps', 'gz_dps']].values
y = df['label'].values

print("Normalizing...")
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)
joblib.dump(scaler, 'scaler.pkl')
print("Scaler saved.")

print(f"Total records: {len(df)}")
print(f"Good records: {good_df.shape[0]}")
print(f"Bad records: {bad_df.shape[0]}")

model = keras.Sequential([
    keras.layers.Input(shape=(6,)),
    keras.layers.Dense(8, activation='relu'),
    keras.layers.Dense(1, activation='sigmoid')
])

print("1")
model.compile(optimizer=Adam(learning_rate=0.00001), loss='binary_crossentropy', metrics=['accuracy'])
print("2")
model.fit(X_scaled, y, epochs=3, batch_size=16, validation_split=0.2)
model.save("update_ready_model01large.keras")

try:
    model.save("update_ready_model1.h5")
except:
    pass