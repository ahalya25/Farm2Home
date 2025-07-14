import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, 'ml_models', 'product_quality_model.h5')

logging.info(f"Attempting to load model from: {model_path}")

model = None
try:
    model = load_model(model_path)
    logging.info("Model loaded successfully.")
except Exception as e:
    logging.error(f"Error loading Keras model from {model_path}: {e}")
    model = None

def predict_freshness(img_path):
    if not os.path.exists(img_path):
        logging.error(f"Image file not found at: {img_path}")
        return 'Prediction Error: Image Not Found'

    if model is None:
        logging.error("AI model not loaded. Cannot perform prediction.")
        return 'Prediction Error: Model Not Loaded'

    try:
        logging.info(f"Processing image: {img_path}")
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0

        prediction = model.predict(img_array)

        # --- CRITICAL DEBUGGING LINE: This output is essential ---
        logging.info(f"Full raw prediction array (before argmax): {prediction}")
        # --- END CRITICAL DEBUGGING LINE ---

        # Define your target classes for display
        # Note: 'Moderate' is included for consistency with Product model,
        # but will not be directly returned by the binary classification logic below.
        target_classes = ['Fresh','Stale']

        if prediction.size == 0:
            logging.error("Model returned an empty prediction array.")
            return 'Prediction Error: Empty Prediction'

        predicted_class = 'Prediction Error: Unknown Output' # Default error

        if prediction.shape[1] == 1:
            # Model outputs a single probability (e.g., probability of being 'good' or 'fresh')
            # This is common for binary classification with sigmoid activation (output range 0 to 1)
            probability_of_positive_class = prediction[0][0] # Assuming higher value means 'good'/'fresh'
            logging.info(f"Model output is binary (1 neuron). Probability of positive class: {probability_of_positive_class:.4f}")

            # --- Binary Classification Logic (Fresh or Stale only) ---
            # If the probability of the positive class is above 0.5, classify as 'Fresh', otherwise 'Stale'.
            # If your model is consistently outputting < 0.5 for fresh images, the issue is with the model's training.
            if probability_of_positive_class >= 0.5:
                predicted_class = 'Fresh'
            else:
                predicted_class = 'Stale'

        elif prediction.shape[1] == 2:
            # Model outputs two probabilities (e.g., [prob_class_0, prob_class_1])
            # This is common for binary classification with softmax activation
            # You MUST know what index 0 and index 1 represent in YOUR trained model.
            # Based on your 'bad' and 'good' folders, a common assumption is:
            # prediction[0][0] is probability of 'Stale/Bad'
            # prediction[0][1] is probability of 'Fresh/Good'
            prob_stale_bad = prediction[0][0]
            prob_fresh_good = prediction[0][1]
            logging.info(f"Model output is binary (2 neurons). Probabilities: [Stale/Bad: {prob_stale_bad:.4f}, Fresh/Good: {prob_fresh_good:.4f}]")

            # --- Binary Classification Logic (Fresh or Stale only) ---
            # Classify based on which probability is higher.
            # If prob_fresh_good is consistently lower than prob_stale_bad for fresh images, the issue is with the model's training.
            if prob_fresh_good > prob_stale_bad:
                predicted_class = 'Fresh'
            else:
                predicted_class = 'Stale'

        elif prediction.shape[1] == 3:
            # This block is for true multi-class models (3 outputs)
            # If your model was re-trained to output 3 classes, this is the correct block.
            # Ensure classes_order_in_model matches your model's output neuron order.
            classes_order_in_model = ['Fresh','Stale'] # Example order, confirm with your model's training

            predicted_index = np.argmax(prediction)
            logging.info(f"Predicted index (from argmax): {predicted_index}")

            if 0 <= predicted_index < len(classes_order_in_model):
                predicted_class = classes_order_in_model[predicted_index]
            else:
                logging.error(f"Predicted index {predicted_index} out of bounds for classes {classes_order_in_model}.")
                predicted_class = 'Prediction Error: Invalid Mapped Index'
        else:
            logging.error(f"Model output shape {prediction.shape} is unexpected. Expected 1, 2, or 3 outputs.")
            predicted_class = 'Prediction Error: Unexpected Output Shape'

        logging.info(f"Final predicted class: {predicted_class}")
        return predicted_class

    except Exception as e:
        logging.error(f"An error occurred during prediction for {img_path}: {e}", exc_info=True)
        return 'Prediction Error: Internal'
