from django.urls import path
from . import views

urlpatterns = [
    path('enroll-confirmation/<uuid:uuid>/', views.EnrollConfirmationView.as_view(), name='enroll-confirmation'),
    path('razorpay-view/<uuid:uuid>/', views.RazorpayView.as_view(), name='razorpay-view'),
    path('verify-payment/', views.PaymentverifyView.as_view(), name='payment-verify'),
    path('checkout/', views.CartCheckoutView.as_view(), name='cart_check-out'),
]
