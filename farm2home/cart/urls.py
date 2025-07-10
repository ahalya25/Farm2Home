from django.urls import path
import uuid
from . import views

urlpatterns = [

    path('cart/<str:uuid>/',views.AddToCartView.as_view(),name='cart'),
]
