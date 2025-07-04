from django.shortcuts import render,redirect

# Create your views here.
from django.views import View

from .models import Product

class ProductListView(View):

    def get(self,request,*args,**kwargs):

        product = Product.objects.all()
        
        data = {'product':product, 'page':'product-page'}

        return render(request,'marketplace/product-list.html')

class HomeView(View):

    def get(self,request,*args,**kwargs):

        data ={'page': 'home-page'} 

        return render(request,'marketplace/home.html',context=data)
    
class ProductDetailView(View):

    def get(self,request,*args,**kwargs):

        uuid = kwargs.get('uuid')

        product = Product.objects.get(uuid=uuid)

        # recommended_product = get_recommended_product(product)

        data = {'product' : product }

        return render(request,'marketplace/product-detail.html',context=data)     
        