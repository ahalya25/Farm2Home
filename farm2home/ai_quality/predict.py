import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Define base directory of this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path to your AI model file inside ml_model folder
model_path = os.path.join(BASE_DIR, 'ml_models', 'product_quality_model.h5')

print(f"Loading model from: {model_path}")  # Optional debug

# Load the trained Keras model
model = load_model(model_path)


def predict_freshness(img_path):
    

    # Load image with target size (adjust size to what your model expects)
    img = image.load_img(img_path, target_size=(224, 224))

    # Convert image to array
    img_array = image.img_to_array(img)

    # Expand dims to match model input shape (batch size 1)
    img_array = np.expand_dims(img_array, axis=0)

    # Normalize image pixels (0 to 1)
    img_array = img_array / 255.0

    # Get prediction probabilities from model
    prediction = model.predict(img_array)

    # Define your classes (update according to your model's output classes)
    classes = ['Stale', 'Moderate', 'Fresh']

    # Get index of highest probability
    predicted_index = np.argmax(prediction)

    # Return predicted class label
    return classes[predicted_index]
