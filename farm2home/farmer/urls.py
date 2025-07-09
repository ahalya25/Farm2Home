from django.urls import path

from uuid import UUID

from . import views

urlpatterns =[

        path('farmer-register/',views.FarmerRegisterView.as_view(),name='farmer-register'),

        path('farmer-product-detail/<str:uuid>/',views.FarmerProductDetailView.as_view(), name='farmer-product-detail'),

        path('farmer-product-list/',views.FarmerProductListView.as_view(),name='farmer-product-list'),

        path('farmer-product-update/<str:uuid>/',views.FarmerProductUpdateView.as_view(),name='farmer-product-update'),
        
        path('farmer-product-delete/<str:uuid>/',views.FarmerProductDeleteView.as_view(),name='farmer-product-delete'),

]
