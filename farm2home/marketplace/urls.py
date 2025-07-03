from django.urls import path

from . import views

urlpatterns =[

    path('product-list/',views.ProductListView.as_view()),
    
    path('home/',views.HomeView.as_view(),name='home'),
]