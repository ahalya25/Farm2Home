from django.shortcuts import render

# Create your views here.
from django.views import View

class MarketPlacesListView(View):

    def get(self,request,*args,**kwargs):

        return render(request,'marketplace/marketplace-list.html')

