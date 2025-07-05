from django.urls import path

from . import views

urlpatterns =[

        path('farmer-register/',views.FarmerRegisterView.as_view(),name='farmer-register'),

        path('farmer-product-detail/<str:uuid>/',views.FarmerProductDetailView.as_view(),name='farmer-product-detail'),
        
        path('farmer-product-delete/<str:uuid>/',views.FarmerProductDeleteView.as_view(),name='farmer-product-delete'),

]
