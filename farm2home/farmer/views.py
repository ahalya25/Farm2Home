from django.shortcuts import render ,redirect

from django.views import View

from .forms import FarmerForm 

from  consumer.forms import ProfileForm

from django.db import transaction 

from farm2home.utility import send_email

from django.contrib.auth.hashers import make_password

from  marketplace.models import Product

from marketplace.forms import ProductAddForm

from django.utils.decorators import method_decorator

from authentication.permissions import permission_roles

from django.db.models import Q

from marketplace.models import Product

from .models import Farmer

import threading

import uuid


# Create your views here.
class FarmerRegisterView(View):

    def get(self,request,*args,**kwargs):

        profile_form = ProfileForm()

        farmer_form = FarmerForm()

        data = {'profile_form' : profile_form,'farmer_form': farmer_form}

        return render(request,'farmer/farmer-register.html',context=data)
    
    
    def post(self, request, *args , **kwargs):

        profile_form = ProfileForm(request.POST)

        print(profile_form.errors)

        farmer_form = FarmerForm(request.POST, request.FILES)

        print(farmer_form.errors)

        if profile_form.is_valid():

            with transaction.atomic():

                profile = profile_form.save(commit=False)

                email = profile_form.cleaned_data.get('email')

                password = profile_form.cleaned_data.get('password')

                profile.username = email

                profile.role = 'Farmer'

                profile.password = make_password(password)

                profile.save()


                if  farmer_form.is_valid():

                    farmer = farmer_form.save(commit=False)

                    farmer.profile = profile

                    farmer.name = f'{profile.first_name} {profile.last_name}'

                    farmer.save()

                    subject = 'Successfully Registered'

                    recipient = farmer.profile.email

                    template = 'email/success-registertion.html'

                    context = {'name': farmer.name,'username': farmer.profile.email,'password':password }

                    thread = threading.Thread(target=send_email,args=(subject,recipient,template,context))

                    # send_email(subject,recipient,template,context)

                    thread.start()

                    return redirect('login')
            
            data = {'profile_form' : profile_form, 'farmer_form': farmer_form}

            return render(request,'farmer/farmer-register.html',context=data)
        


class FarmerProductListView(View):

    def get(self, request, *args, **kwargs):

        query = request.GET.get('query')
        
        farmer = Farmer.objects.get(profile=request.user) 

        product = Product.objects.filter(farmer=farmer)

       
        # product = Product.objects.filter(farmer=farmer)

        if query:

            product = Product.objects.filter(Q(farmer=farmer) & (Q(product_name__icontains=query)|
                                             Q(price__icontains=query)|
                                             Q(offer_price__icontains=query)|
                                             Q(quantity__icontains=query)|
                                             Q(freshness__icontains=query)|
                                             Q(created_at__icontains=query)))
            
        print(product)    
                                             
        
        data = {'product': product, 'page' : 'farmer-product-page',query : query}

        return render(request,'farmer/farmer-product-list.html', context=data)

        
# @method_decorator(permission_roles(roles=['Farmer']),name='dispatch')
class FarmerProductDetailView(View):

    def get(self,request,*args,**kwargs):

        uuid = kwargs.get('uuid')

        product = Product.objects.get(uuid=uuid)

        data = {'product' : product }

        return render(request,'farmer/farmer-product-detail.html',context=data) 
    


# @method_decorator(permission_roles(roles=['Farmer']),name='dispatch')
class FarmerProductUpdateView(View):

    def get(self,request,*args,**kwargs):

        uuid = kwargs.get('uuid')

        product = Product.objects.get(uuid=uuid)

        form = ProductAddForm(instance=product)

        data = {'form' : form }

        return render(request,'farmer/farmer-product-update.html',context=data) 

    def post(self,request,*args,**kwargs) :

        uuid = kwargs.get('uuid')

        product = Product.objects.get(uuid=uuid) 

        form = ProductAddForm(request.POST,request.FILES,instance=product)

        if form.is_valid(): # check for data is valid

            form.save()  

            return redirect('farmer-product-list') 

        data = {'form' : form }

        return render(request,'farmer/farmer-product-update.html',context = data)             


# # @method_decorator(permission_roles(roles=['farmer']),name='dispatch')
class FarmerProductDeleteView(View):

    def get(self,request,*args,**kwargs):

        uuid =kwargs.get('uuid') #pick id

        product = Product.objects.get(uuid=uuid) #orm 

        product.delete()

        return redirect('product-list')
        #change to farmer-product-list


    
    