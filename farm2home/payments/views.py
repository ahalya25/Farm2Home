# Create your views here.
from django.shortcuts import render ,redirect

from django.views import View

from .models import Payments

from marketplace.models import Product

from consumer.models import Consumer

from .models import Payments , Transactions

import razorpay

import datetime

from decouple import config

# from .models import Transactions

# import razorpay

from decouple import config

class EnrollConfirmationView(View):

    def get(self,request,*args,**kwargs):

        uuid = kwargs.get('uuid')

        product = Product.objects.get(uuid = uuid)

        payment,created = Payments.objects.get_or_create(consumer=Consumer.objects.get(profile=request.user),product=product,
                                      amount=product.offer_price if product.offer_price else product.price)

        data = { 'payment' : payment }

        return render(request,'payments/enroll-confirmation.html',context=data)

class RazorpayView(View):

    def get(self, request, *args, **kwargs): 

         uuid = kwargs.get('uuid')

         product = Product.objects.get(uuid=uuid)

         payment = Payments.objects.get(consumer__profile=request.user, product=product)

         transaction = Transactions.objects.create(payment=payment)

         client = razorpay.Client(auth=(config("RZP_CLIENT_ID"), config("RZP_CLIENT_SECRET")))

         data = { "amount": payment.amount*100, "currency": "INR", "receipt": "order_rcptid_11" }
        
         order = client.order.create(data=data)  

         print(order)

         rzp_order_id = order.get('id')

         transaction.rzp_order_id = rzp_order_id

         transaction.save()

         data = {'client_id' : config("RZP_CLIENT_ID"), 'rzp_order_id' : rzp_order_id ,'amount' : payment.amount*100}

         return render(request,'payments/payment-page.html', context=data)

    

class PaymentverifyView(View):
       #checking for transaction is correct or not

    def post(self,request,*args,**kwargs):

        # print(request.POST)

        rzp_order_id = request.POST.get('razorpay_order_id')

        rzp_payment_id = request.POST.get('razorpay_payment_id')

        rzp_payment_signature = request.POST.get('razorpay_signature')

        client = razorpay.Client(auth=(config("RZP_CLIENT_ID"), config("RZP_CLIENT_SECRET")))

        transaction = Transactions.objects.get(rzp_order_id = rzp_order_id) 

        time_now = datetime.datetime.now()

        transaction.rzp_payment_id = rzp_payment_id

        transaction.rzp_payment_signature = rzp_payment_signature

        try:
            
            client.utility.verify_payment_signature({
                                                
                                                'razorpay_order_id': rzp_order_id,
                                                'razorpay_payment_id': rzp_payment_id,
                                                'razorpay_signature': rzp_payment_signature
                                                })
            
           
            transaction.status= 'Success'

            transaction.save()

            transaction.payment.status = 'Success'

            transaction.payment.paid_at = time_now

            transaction.payment.save()

            return redirect('home')     
            
        except :    

            transaction.status= 'Failed'

            transaction.payment.save()
            
            transaction.save()

            return redirect('razorpay-view',uuid=transaction.payment.product.uuid)
                


    

