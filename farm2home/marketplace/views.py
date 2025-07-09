from django.shortcuts import render,redirect

# Create your views here.
from django.views import View

from .models import Product

from .forms import ProductAddForm

from farmer.models import Farmer

from django.db.models import Q

from django.contrib.auth.decorators import login_required

from django.utils.decorators import method_decorator

from authentication.permissions import permission_roles


class ProductListView(View):

    def get(self, request, *args, **kwargs):

        query = request.GET.get('query')

        product = Product.objects.all()

        if query:
            
            product = Product.objects.filter(
                Q(product_name__icontains=query) |
                Q(price__icontains=query) |
                Q(quantity__icontains=query) |
                Q(freshness__icontains=query) |
                Q(created_at__icontains=query)
            )

        data = {'products': product, 'page': 'product-page', 'query': query}

        return render(request, 'marketplace/product-list.html', context=data)

class HomeView(View):

    def get(self,request,*args,**kwargs):

        data ={'page': 'home-page'} 

        return render(request,'marketplace/home.html',context=data)
    

@method_decorator(permission_roles(roles=['Farmer']),name='dispatch')    
class ProductAddView(View):

    def get(self,request,*args,**kwargs):

        form = ProductAddForm()

        data = {'form' : form }    

        return render(request,'marketplace/product-add.html',context=data)
    

    def post(self,request,*args,**kwargs):      

        form = ProductAddForm(request.POST,request.FILES)

        farmer = Farmer.objects.get(id=1)

        if form.is_valid():

            product = form.save(commit=False)

            product.farmer = farmer

            product.save()

            return redirect('farmer-product-list')
        
        data = {'form' : form }
        
        return render(request,'marketplace/product-add.html',context=data)
    

        
# @method_decorator(login_required(login_url='login'),name='dispatch')  
class ProductDetailView(View):

    def get(self,request,*args,**kwargs):

        uuid = kwargs.get('uuid')

        product = Product.objects.get(uuid=uuid)

        # recommended_product = get_recommended_product(product)

        data = {'product' : product }

        return render(request, 'marketplace/product-detail.html', context=data)    



        