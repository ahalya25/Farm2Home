from django.urls import path
from .views import check_quality, FarmerQualityView

urlpatterns = [
    path('check-quality/', check_quality, name='check_quality'),
    path('farmer/upload/', FarmerQualityView.as_view(), name='farmer_upload'),
]
