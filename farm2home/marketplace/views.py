from django.shortcuts import render,redirect

# Create your views here.
from django.views import View

class ProductListView(View):

    def get(self,request,*args,**kwargs):

        # product

        return render(request,'marketplace/product-list.html')

