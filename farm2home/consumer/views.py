from django.shortcuts import render , redirect

# Create your views here.
from .forms import ConsumerForm

from django.views import View

from  consumer.forms import ProfileForm

from django.db import transaction 

from farm2home.utility import send_email

from django.contrib.auth.hashers import make_password

import threading


class ConsumerRegisterView(View):

    def get(self,request,*args,**kwargs):

        profile_form = ProfileForm()

        consumer_form = ConsumerForm()

        data = {'profile_form' : profile_form,'consumer_form': consumer_form}

        return render(request,'consumer/consumer-register.html',context=data)
    
    def post(self, request, *args , **kwargs):

        profile_form = ProfileForm(request.POST)

        print(profile_form.errors)

        consumer_form = ConsumerForm(request.POST, request.FILES)

        print(consumer_form.errors)

        if profile_form.is_valid():

            with transaction.atomic():

                profile = profile_form.save(commit=False)

                email = profile_form.cleaned_data.get('email')

                password = profile_form.cleaned_data.get('password')

                profile.username = email

                profile.role = 'Consumer'

                profile.password = make_password(password)

                profile.save()


                if  consumer_form.is_valid():

                    consumer = consumer_form.save(commit=False)

                    consumer.profile = profile

                    consumer.name = f'{profile.first_name} {profile.last_name}'

                    consumer.save()

                    subject = 'Successfully Registered'

                    recipient = consumer.profile.email

                    template = 'email/success-registertion.html'

                    context = {'name': consumer.name,'username': consumer.profile.email,'password':password }

                    thread = threading.Thread(target=send_email,args=(subject,recipient,template,context))

                    send_email(subject,recipient,template,context)
                    
                    thread.start()

                    return redirect('login')
            
            data = {'profile_form' : profile_form, 'farmer_form': consumer_form}

            return render(request,'consumer/consumer-register.html',context=data)
    
    