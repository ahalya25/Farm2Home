import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os

# Set paths
train_dir = 'data/train'
val_dir = 'data/val'

# Check that folders exist
if not os.path.exists(train_dir) or not os.path.exists(val_dir):
    raise Exception("Make sure you have data/train/good, data/train/bad, data/val/good, data/val/bad folders with images.")

# Data preprocessing & augmentation for training
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    zoom_range=0.2,
    horizontal_flip=True
)

# Only rescale for validation
val_datagen = ImageDataGenerator(rescale=1./255)

# Create training generator
train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='binary'  # good vs bad
)

# Create validation generator
val_generator = val_datagen.flow_from_directory(
    val_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='binary'
)

# Load MobileNetV2 as base model
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False  # Freeze base model

# Build full model
model = tf.keras.Sequential([
    base_model,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(1, activation='sigmoid')  # Binary classification: good/bad
])

# Compile the model
model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# Train the model
model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=5
)

# Save the trained model
os.makedirs('ml_models', exist_ok=True)
model.save('ml_models/product_quality_model.h5')

print("✅ Model training complete. Saved to 'ml_models/product_quality_model.h5'")
