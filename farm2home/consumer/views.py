from django.shortcuts import render

# Create your views here.
from .forms import ConsumerForm

from django.views import View

from  consumer.forms import ProfileForm

class ConsumerRegisterView(View):

    def get(self,request,*args,**kwargs):

        profile_form = ProfileForm()

        consumer_form = ConsumerForm()

        data = {'profile_form' : profile_form,'consumer_form': consumer_form}

        return render(request,'consumer/consumer-register.html',context=data)