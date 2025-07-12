# predict.py
from PIL import Image
import numpy as np

def predict_freshness(image_field):
    image = Image.open(image_field)
    image = image.resize((100, 100))  # resize if needed
    img_array = np.array(image)

    # Dummy AI logic for example
    if img_array.mean() > 127:
        return "Fresh"
    else:
        return "Not Fresh"
