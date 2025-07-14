# ai_quality/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('quality-check/', views.FarmerQualityView.as_view(), name='quality-check'),
]
