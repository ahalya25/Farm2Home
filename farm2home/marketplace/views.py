from django.shortcuts import render,redirect

# Create your views here.
from django.views import View

from .models import Product

from .forms import ProductAddForm

from django.contrib import messages

from farmer.models import Farmer

from django.db.models import Q

from django.contrib.auth.decorators import login_required 

from django.utils.decorators import method_decorator

from authentication.permissions import permission_roles

from .forms import ProductAddForm

from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import CreateView
from ai_quality.predict import predict_freshness
from django.conf import settings
import os
from django.core.files.storage import default_storage 
import logging
 
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
    
  # import your AI function at top of views.py



# @method_decorator(permission_roles(roles=['Farmer']), name='dispatch') 
class ProductAddView(View):
    def get(self, request, *args, **kwargs):
        form = ProductAddForm()
        return render(request, 'marketplace/product-add.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = ProductAddForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save(commit=False)

            uploaded_file = request.FILES.get('image')
            if not uploaded_file:
                messages.error(request, 'Please upload an image for the product.')
                return render(request, 'marketplace/product-add.html', {'form': form})

            file_path = default_storage.save(f'temp/{uploaded_file.name}', uploaded_file)
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)

            quality = None # Initialize quality to None
            try:
                # Call the AI prediction function
                quality = predict_freshness(full_path)
                logging.info(f"AI Prediction Result: {quality}") # Log the result
            except Exception as e:
                logging.error(f"Prediction error during product add: {str(e)}", exc_info=True)
                messages.error(request, f'Prediction error: {str(e)}. Please try again.')
                # Do NOT return here, allow product to save without freshness if prediction fails
            finally:
                # Ensure the temporary file is removed
                if os.path.exists(full_path):
                    os.remove(full_path)

        
            product.freshness = quality

            # --- FIX FOR FARMER NAME ---
            try:
                # Retrieve the Farmer instance linked to the current user's Profile
                farmer = Farmer.objects.get(profile=request.user)

                # If farmer_name is empty, populate it from the user's first_name or username
                if not farmer.farmer_name: # Checks if the field is empty
                    if request.user.first_name and request.user.last_name:
                        farmer.farmer_name = f"{request.user.first_name} {request.user.last_name}"
                    elif request.user.first_name:
                        farmer.farmer_name = request.user.first_name
                    else:
                        farmer.farmer_name = request.user.username # Fallback to username
                    farmer.save() # Save the Farmer object if its name was updated
                    logging.info(f"Updated farmer_name for {farmer.profile.username} to: {farmer.farmer_name}")

            except Farmer.DoesNotExist:
                messages.error(request, 'No Farmer account associated with your profile. Please ensure you are logged in as a farmer.')
                return render(request, 'marketplace/product-add.html', {'form': form})
            except Exception as e:
                logging.error(f'An unexpected error occurred while fetching/updating farmer details: {str(e)}', exc_info=True)
                messages.error(request, f'An error occurred with farmer details: {str(e)}')
                return render(request, 'marketplace/product-add.html', {'form': form})
            # --- END FIX FOR FARMER NAME ---

            product.farmer = farmer
            product.save()

            messages.success(request, 'Product added successfully!')
            return redirect('product-list')
        else:
            messages.error(request, 'Please correct the errors below.')
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



        