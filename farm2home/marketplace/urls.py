from django.urls import path
from uuid import UUID  # optional, good for clarity

from . import views

urlpatterns =[

    path('product-list/',views.ProductListView.as_view(),name='product-list'),
    
    path('home/',views.HomeView.as_view(),name='home'),

    path('farmer/upload-success/',views.upload_success,name='upload_success'),

    path('products/<uuid:uuid>/', views.ProductDetailView.as_view(), name='product-detail'),

    path('product-add/',views.ProductAddView.as_view(),name='product-add'),
]