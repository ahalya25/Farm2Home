from django.urls import path

from . import views

urlpatterns =[

    path('consumer-register',views.ConsumerRegisterView.as_view(),name='consumer-register')

   
]