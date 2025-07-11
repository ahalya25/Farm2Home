from django.urls import path
import uuid
from . import views

urlpatterns = [

path('cart/add/<str:uuid>/', views.AddToCartView.as_view(), name='cart'),
path('cart/', views.CartDetailView.as_view(), name='cart-page'),
path('cart/increase/<int:cart_id>/', views.IncreaseQuantityView.as_view(), name='cart-increase'),
path('cart/decrease/<int:cart_id>/', views.DecreaseQuantityView.as_view(), name='cart-decrease'),



]
