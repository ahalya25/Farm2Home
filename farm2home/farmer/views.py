from django.shortcuts import render ,redirect

from django.views import View

from .forms import FarmerForm 

from  consumer.forms import ProfileForm


# Create your views here.
class FarmerRegisterView(View):

    def get(self,request,*args,**kwargs):

        profile_form = ProfileForm()

        farmer_form = FarmerForm()

        data = {'profile_form' : profile_form,'farmer_form': farmer_form}

        return render(request,'farmer/farmer-register.html',context=data)
    
    