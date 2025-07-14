# train_model.py
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Data folders
train_dir = 'dataset/train'
val_dir = 'dataset/val'

img_size = (100, 100)
batch_size = 32

# Image preprocessing
train_gen = ImageDataGenerator(rescale=1./255).flow_from_directory(
    train_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='binary'  # Binary classification (0 = bad, 1 = good)
)

val_gen = ImageDataGenerator(rescale=1./255).flow_from_directory(
    val_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='binary'
)

# CNN model
model = Sequential([
    Conv2D(32, (3,3), activation='relu', input_shape=(100, 100, 3)),
    MaxPooling2D(),
    Flatten(),
    Dense(64, activation='relu'),
    Dense(1, activation='sigmoid')  # Only 1 neuron with sigmoid for binary output
])

# Compile
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train
model.fit(train_gen, epochs=10, validation_data=val_gen)

# Save model
model.save('quality_model.h5')
