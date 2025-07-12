from django.shortcuts import render
import tensorflow as tf
from tensorflow.keras.utils import load_img, img_to_array
import numpy as np
import os
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from marketplace.models import Product
from marketplace.forms import ProductAddForm

# Load model once
model = tf.keras.models.load_model('ml_models/product_quality_model.h5')


def check_quality(request):
    result = None

    if request.method == 'POST' and request.FILES.get('image'):
        img_file = request.FILES['image']
        img_path = 'media/uploads/' + img_file.name

        # Save image
        os.makedirs('media/uploads', exist_ok=True)
        with open(img_path, 'wb+') as f:
            for chunk in img_file.chunks():
                f.write(chunk)

        # Load and preprocess image
        img = load_img(img_path, target_size=(224, 224))
        img_array = img_to_array(img)
        img_array = img_array / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = model.predict(img_array)[0][0]
        result = 'Good' if prediction < 0.5 else 'Bad'

    return render(request, 'upload_quality.html', {'result': result})



# Dummy AI prediction function – you’ll replace this later with real AI
def run_ai_quality_prediction(image_file):
    import random
    return random.choice(['Fresh', 'Moderate', 'Stale'])

class FarmerQualityView(LoginRequiredMixin, UserPassesTestMixin, CreateView):

    model = Product
    form_class = ProductAddForm
    template_name = 'farmer_upload.html'
    success_url = '/farmer/upload-success/'

    def form_valid(self, form):
        product = form.save(commit=False)
        product.farmer = self.request.user.farmer  # Assuming OneToOne between user and farmer
        image_file = self.request.FILES['image']
        product.freshness = run_ai_quality_prediction(image_file)
        product.save()
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.role == 'Farmer'
    


