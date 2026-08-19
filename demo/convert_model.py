import tensorflow as tf

# Load the model
model = tf.keras.models.load_model('update_ready_model01large.keras')

# Convert to TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Save the TFLite model
with open('model.tflite', 'wb') as f:
    f.write(tflite_model)

print(f"TFLite model saved, size: {len(tflite_model)} bytes")