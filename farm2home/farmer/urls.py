from django.urls import path

from . import views

urlpatterns =[

        path('farmer-register/',views.FarmerRegisterView.as_view(),name='farmer-register')

]
