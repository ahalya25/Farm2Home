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
from order.models import Orders
from consumer.models import Consumer
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


class RazorpayView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            consumer = Consumer.objects.get(profile=request.user)
        except Consumer.DoesNotExist:
            raise Http404("Consumer not found.")

        cart_items = Cart.objects.filter(user=consumer)

        if not cart_items.exists():
            messages.info(request, "Your cart is empty. Please add items before proceeding to payment.")
            return redirect('product-list')  # Redirect to product list or cart page

        # Calculate total amount considering offer_price if available
        total_amount = 0
        for item in cart_items:
            price = item.product.offer_price if item.product.offer_price else item.product.price
            total_amount += price * item.quantity

        if total_amount <= 0:
            messages.error(request, "Cannot proceed with payment for an empty or zero-value cart.")
            return redirect('cart_check-out')

        try:
            # Get or create a pending payment
            payment, created = Payments.objects.get_or_create(
                consumer=consumer,
                status='Pending',
                defaults={'amount': total_amount, 'paid_at': None}
            )
            if not created:
                # Update amount if pending payment already exists
                payment.amount = total_amount
                payment.save()
        except Exception as e:
            logging.error(f"Error getting or creating payment: {e}")
            raise Http404("Could not prepare payment.")

        # Create a new transaction linked to this payment
        transaction = Transactions.objects.create(payment=payment)

        # Initialize Razorpay client
        client = razorpay.Client(auth=(config("RZP_CLIENT_ID"), config("RZP_CLIENT_SECRET")))

        order_data = {
            "amount": int(payment.amount * 100),  # Razorpay expects amount in paise
            "currency": "INR",
            "receipt": f"order_rcptid_{transaction.id}",
        }

        try:
            order = client.order.create(data=order_data)
            transaction.rzp_order_id = order.get('id')
            transaction.save()
        except Exception as e:
            logging.error(f"Razorpay order creation failed: {e}")
            messages.error(request, "Failed to create payment order. Please try again.")
            return redirect('cart_check-out')

        context = {
            'client_id': config("RZP_CLIENT_ID"),
            'rzp_order_id': transaction.rzp_order_id,
            'amount': int(payment.amount * 100),
            'consumer_phone': consumer.phone,  # Ensure this field exists
            'consumer_email': request.user.email,
            'payment': payment,
            'cart_items': cart_items,
            'total_amount': total_amount,
        }

        return render(request, 'payments/payment-page.html', context)

class PaymentverifyView(View):
    def post(self, request, *args, **kwargs):
        rzp_order_id = request.POST.get('razorpay_order_id')
        rzp_payment_id = request.POST.get('razorpay_payment_id')
        rzp_payment_signature = request.POST.get('razorpay_signature')

        client = razorpay.Client(auth=(config("RZP_CLIENT_ID"), config("RZP_CLIENT_SECRET")))

        transaction = None  # Initialize to avoid reference before assignment

        try:
            transaction = Transactions.objects.get(rzp_order_id=rzp_order_id)

            # Verify signature
            client.utility.verify_payment_signature({
                'razorpay_order_id': rzp_order_id,
                'razorpay_payment_id': rzp_payment_id,
                'razorpay_signature': rzp_payment_signature,
            })

            # Update transaction & payment status
            transaction.rzp_payment_id = rzp_payment_id
            transaction.rzp_payment_signature = rzp_payment_signature
            transaction.status = 'Success'
            transaction.save()

            payment = transaction.payment
            payment.status = 'Success'
            payment.paid_at = datetime.datetime.now()
            payment.save()

            # ✅ Get Profile from Consumer
            consumer_profile = payment.consumer.profile

            # ✅ Create orders
            cart_items = Cart.objects.filter(user=payment.consumer)
            for item in cart_items:
                Orders.objects.create(
                    consumer=consumer_profile,  # ✅ Corrected here
                    product=item.product,
                    quantity=item.quantity
                )

            cart_items.delete()

            messages.success(request, "Your payment was successful and your order has been placed!")
            return redirect('home')

        except Transactions.DoesNotExist:
            logging.error(f"Payment verification failed: Transaction with order ID {rzp_order_id} not found.")
            messages.error(request, "Payment verification failed: Invalid transaction.")
            return HttpResponseBadRequest("Invalid transaction")

        except Exception as e:
            logging.error(f"Payment verification failed for order {rzp_order_id}: {e}")
            messages.error(request, f"Payment verification failed: {e}. Please try again.")

            try:
                if transaction:
                    transaction.status = 'Failed'
                    transaction.save()

                    transaction.payment.status = 'Failed'
                    transaction.payment.save()
            except Exception as inner_e:
                logging.error(f"Error marking transaction/payment as failed: {inner_e}")

            if transaction and transaction.payment:
                return redirect('cart_check-out')
            else:
                return redirect('product-list')

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
            total_price = 0
            for item in cart_items:
                # Use offer_price if available, else use product price
                price = item.product.offer_price if item.product.offer_price else item.product.price
                total_price += price * item.quantity

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