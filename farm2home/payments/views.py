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
    """
    Generates Razorpay order and renders payment page with order details.
    """

    def get(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        product = Product.objects.get(uuid=uuid)
        consumer = Consumer.objects.get(profile=request.user)

        # Get existing payment; fail if not exists
        payment = Payments.objects.get(consumer=consumer, product=product)

        # Create a new transaction for this payment attempt
        transaction = Transactions.objects.create(payment=payment)

        client = razorpay.Client(auth=(config("RZP_CLIENT_ID"), config("RZP_CLIENT_SECRET")))

        order_data = {
            "amount": int(payment.amount * 100),  # amount in paise
            "currency": "INR",
            "receipt": f"order_rcptid_{transaction.id}",
        }

        order = client.order.create(data=order_data)
        rzp_order_id = order.get('id')

        transaction.rzp_order_id = rzp_order_id
        transaction.save()

        context = {
            'client_id': config("RZP_CLIENT_ID"),
            'rzp_order_id': rzp_order_id,
            'amount': int(payment.amount * 100),
            'product': product,
            'payment': payment
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
    """
    Handles the checkout process for all items in the user's cart.
    Calculates total amount and initiates Razorpay order.
    """
    def get(self, request, *args, **kwargs):
        consumer = get_object_or_404(Consumer, profile=request.user)
        
        # --- FIX: Change 'consumer' to 'user' for Cart query ---
        # Assuming request.user is the User/Profile object linked to Cart
        cart_items = Cart.objects.filter(user=request.user).select_related('product') # Eagerly load product details

        if not cart_items.exists():
            messages.warning(request, 'Your cart is empty. Please add products before checking out.')
            return redirect('product-list') # Redirect to product list if cart is empty

        # Calculate total amount from cart items
        total_cart_amount = sum(item.total_price for item in cart_items)
        
        if total_cart_amount <= 0:
            messages.error(request, 'Cannot checkout with a zero or negative total amount.')
            return redirect('cart-view')

        # Create or get a Payment object for the entire cart
        try:
            payment, created = Payments.objects.get_or_create(
                consumer=consumer,
                product=None, # Set product to None for cart-wide payment
                status='Pending',
                defaults={'amount': total_cart_amount}
            )
            # If payment already existed and was not pending, or amount changed, update it
            if not created and payment.status == 'Pending':
                payment.amount = total_cart_amount
                payment.save()
            elif not created and payment.status != 'Pending':
                # If an old payment for this consumer (with product=None) is not pending,
                # create a new one to avoid conflicts.
                payment = Payments.objects.create(
                    consumer=consumer,
                    product=None,
                    amount=total_cart_amount,
                    status='Pending'
                )

        except Exception as e:
            logging.error(f"Error creating/getting Payment for cart: {e}", exc_info=True)
            messages.error(request, 'An error occurred while preparing your payment. Please try again.')
            return redirect('cart-view')

        # Create a new transaction for this payment attempt
        transaction = Transactions.objects.create(payment=payment)

        client = razorpay.Client(auth=(config("RZP_CLIENT_ID"), config("RZP_CLIENT_SECRET")))

        order_data = {
            "amount": int(payment.amount * 100),  # amount in paise
            "currency": "INR",
            "receipt": f"order_rcptid_{transaction.id}",
        }

        try:
            order = client.order.create(data=order_data)
            rzp_order_id = order.get('id')
        except Exception as e:
            logging.error(f"Error creating Razorpay order: {e}", exc_info=True)
            messages.error(request, 'Failed to create payment order. Please try again later.')
            transaction.status = 'Failed'
            transaction.save()
            return redirect('cart-view')

        transaction.rzp_order_id = rzp_order_id
        transaction.save()

        context = {
            'client_id': config("RZP_CLIENT_ID"),
            'rzp_order_id': rzp_order_id,
            'amount': int(payment.amount * 100),
            'product': None, # No specific product for cart-wide payment
            'payment': payment,
            'consumer_email': request.user.email, # For Razorpay prefill
            'consumer_phone': consumer.phone # Assuming Consumer model has a phone field
        }
        return render(request, 'payments/payment-page.html', context) # Reuse payment-page.html

