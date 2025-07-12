from django.shortcuts import render,redirect

# Create your views here.
from django.views import View

from .models import Product

from .forms import ProductAddForm

from farmer.models import Farmer

from django.db.models import Q

from django.contrib.auth.decorators import login_required 

from django.views.generic.edit import CreateView

from django.utils.decorators import method_decorator

from authentication.permissions import permission_roles

from .forms import ProductAddForm

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class FarmerQualityView(LoginRequiredMixin, UserPassesTestMixin, CreateView):

    model = Product

    form_class = ProductAddForm

    template_name = 'farmer_upload.html'

    success_url = '/farmer/upload-success/'  # You can customize this

    def form_valid(self, form):

        product = form.save(commit=False)
        product.farmer = self.request.user.farmer  # Assuming request.user is linked to farmer
        image_file = self.request.FILES['image']
        product.quality = run_ai_quality_prediction(image_file)
        product.save()
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.role == 'Farmer'



class ProductListView(View):

    def get(self, request, *args, **kwargs):

        query = request.GET.get('query')

        product = Product.objects.all()

        if query:
            
            product = Product.objects.filter(
                
                Q(farmer__farmer_name__icontains=query)|
                Q(product_name__icontains=query) |
                Q(price__icontains=query) |
                Q(quantity__icontains=query) |
                Q(freshness__icontains=query) |
                Q(created_at__icontains=query)
            )

        data = {'products': product, 'page': 'product-page', 'query': query}

        return render(request,'marketplace/product-list.html', context=data)

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
    
    
    def post(self, request, *args, **kwargs):
     
     form = ProductAddForm(request.POST, request.FILES)

     if form.is_valid():
        
        product = form.save(commit=False)

        try:
            farmer = Farmer.objects.get(profile=request.user)

        except Farmer.DoesNotExist:

            return render(request, 'marketplace/product-add.html', {

                'form': form,

                'error': 'Farmer profile not found for the logged-in user.'
            })

        product.farmer = farmer
        
        product.save()

        return redirect('farmer-product-list')

     return render(request, 'marketplace/product-add.html', {'form': form})


        
# @method_decorator(login_required(login_url='login'),name='dispatch')  
class ProductDetailView(View):

    def get(self,request,*args,**kwargs):

        uuid = kwargs.get('uuid')

        product = Product.objects.get(uuid=uuid)

        # recommended_product = get_recommended_product(product)

        data = {'product' : product }

        return render(request, 'marketplace/product-detail.html', context=data)   



def upload_success(request):
      
    return render(request, 'farmer/upload_success.html')     



        