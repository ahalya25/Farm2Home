import os
from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from django.core.files.storage import default_storage

from ai_quality.predict import predict_freshness  # Your AI logic function
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


# @method_decorator(login_required, name='dispatch')
class FarmerQualityView(View):
    def get(self, request):
        return render(request, 'farmer/farmer_upload.html')

    def post(self, request):
        uploaded_file = request.FILES.get('product_image')

        if not uploaded_file:
            return render(request, 'farmer/farmer_upload.html', {'error': 'Please upload an image.'})

        # Save uploaded file temporarily
        file_path = default_storage.save(f'temp/{uploaded_file.name}', uploaded_file)
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)

        try:
            # Predict the quality using the AI model
            prediction_result = predict_freshness(full_path)
        except Exception as e:
            return render(request, 'farmer/farmer_upload.html', {'error': f'Prediction failed: {str(e)}'})

        # Delete the file after prediction (optional cleanup)
        if os.path.exists(full_path):
            os.remove(full_path)

        # Show result page
        return render(request, 'farmer/upload_success.html', {
            'result': prediction_result
        })
