from django.urls import path

from . import views

urlpatterns =[

    path('marketplace-list/',views.MarketPlacesListView.as_view()),
]