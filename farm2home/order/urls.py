# urls.py
from django.urls import path
from .views import ConsumerDashboardView , FarmerDashboardView

urlpatterns = [
    path('consumer/dashboard/', ConsumerDashboardView.as_view(), name='consumer_dashboard'),
    path('farmer/dashboard/', FarmerDashboardView.as_view(), name='farmer-dashboard'),
   
]
