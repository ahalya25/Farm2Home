from django.shortcuts import render, redirect , get_object_or_404
from django.views import View
from django.http import HttpResponseBadRequest
from decouple import config
import razorpay
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from marketplace.models import Product
from consumer.models import Consumer
from .models import Payments, Transactions
from cart.models import Cart
from django.db.models import Sum # Import Sum for aggregation
import logging 
from django.urls import reverse
from django.contrib import messages
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class EnrollConfirmationView(View):
    

    def get(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        product = Product.objects.get(uuid=uuid)
        consumer = Consumer.objects.get(profile=request.user)

        # Create Payment if not exists
        payment, created = Payments.objects.get_or_create(
            consumer=consumer,
            product=product,
            defaults={'amount': product.offer_price if product.offer_price else product.price,
                      'status': 'Pending'}
        )

        context = {'payment': payment, 'product': product}
        return render(request, 'payments/enroll-confirmation.html', context)


class RazorpayView(View):
    def get(self, request, *args, **kwargs):
        cart_uuid = kwargs.get('uuid')
        
        try:
            cart = Cart.objects.get(uuid=cart_uuid)
        except Cart.DoesNotExist:
            raise Http404("Cart not found")

        product = cart.product

        try:
            consumer = Consumer.objects.get(profile=request.user)
        except Consumer.DoesNotExist:
            raise Http404("Consumer not found")

        try:
            payment, created = Payments.objects.get_or_create(consumer=consumer,product=product,defaults={'amount': product.price} ) # or cart.product.price)
        except Payments.DoesNotExist:
            raise Http404("Payment record not found")

        # Create transaction
        transaction = Transactions.objects.create(payment=payment)

        client = razorpay.Client(auth=(config("RZP_CLIENT_ID"), config("RZP_CLIENT_SECRET")))

        order_data = {
            "amount": int(payment.amount * 100),
            "currency": "INR",
            "receipt": f"order_rcptid_{transaction.id}",
        }

        order = client.order.create(data=order_data)
        transaction.rzp_order_id = order.get('id')
        transaction.save()

        context = {
            'client_id': config("RZP_CLIENT_ID"),
            'rzp_order_id': transaction.rzp_order_id,
            'amount': int(payment.amount * 100),
            'product': product,
            'payment': payment,
        }

        return render(request, 'payments/payment-page.html', context)

class PaymentverifyView(View):
    """
    Verify payment signature posted by Razorpay and update status.
    """

    def post(self, request, *args, **kwargs):
        rzp_order_id = request.POST.get('razorpay_order_id')
        rzp_payment_id = request.POST.get('razorpay_payment_id')
        rzp_payment_signature = request.POST.get('razorpay_signature')

        client = razorpay.Client(auth=(config("RZP_CLIENT_ID"), config("RZP_CLIENT_SECRET")))

        try:
            transaction = Transactions.objects.get(rzp_order_id=rzp_order_id)

            # Verify signature
            client.utility.verify_payment_signature({
                'razorpay_order_id': rzp_order_id,
                'razorpay_payment_id': rzp_payment_id,
                'razorpay_signature': rzp_payment_signature,
            })

            # Update transaction & payment status on success
            transaction.rzp_payment_id = rzp_payment_id
            transaction.rzp_payment_signature = rzp_payment_signature
            transaction.status = 'Success'
            transaction.save()

            payment = transaction.payment
            payment.status = 'Success'
            payment.paid_at = datetime.datetime.now()
            payment.save()

            return redirect('home')  # Redirect to a success or home page

        except Transactions.DoesNotExist:
            return HttpResponseBadRequest("Invalid transaction")

        except Exception as e:
            print(f"Payment verification failed: {e}")

            # Mark transaction and payment as failed
            try:
                transaction.status = 'Failed'
                transaction.save()

                transaction.payment.status = 'Failed'
                transaction.payment.save()
            except:
                pass

            # Redirect back to Razorpay payment page to retry
            return redirect('razorpay-view', uuid=transaction.payment.product.uuid)
        



class CartCheckoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            current_user = request.user
            print("DEBUG: Logged-in user:", current_user)

            # Step 1: Get Consumer object for this user
            try:
                current_consumer = Consumer.objects.get(profile=current_user)
                print("DEBUG: Found consumer:", current_consumer)
            except Consumer.DoesNotExist:
                messages.error(request, "You must register as a consumer to continue.")
                print("DEBUG: Consumer does not exist.")
                return redirect('consumer-register')

            # Step 2: Get cart items for this consumer
            cart_items = Cart.objects.filter(user=current_consumer)
            print("DEBUG: Cart items found:", cart_items.count())

            if not cart_items.exists():
                messages.info(request, "Your cart is empty.")
                return redirect('product-list')

            # Step 3: Calculate total price
            total_price = sum(item.product.price * item.quantity for item in cart_items if item.product is not None)
            print("DEBUG: Total cart value:", total_price)

            # Step 4: Render cart checkout page
            context = {
                'cart_items': cart_items,
                'consumer': current_consumer,
                'total_price': total_price
            }
            return render(request, 'payments/cart_check-out.html', context)

        except Exception as e:
            print("DEBUG: Exception:", e)
            messages.error(request, f"Unexpected error occurred: {e}")
            return redirect('product-list')