from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponseBadRequest
from decouple import config
import razorpay
import datetime

from marketplace.models import Product
from consumer.models import Consumer
from .models import Payments, Transactions


class EnrollConfirmationView(View):
    """
    Display confirmation page for enrollment (purchase).
    Creates Payment object if not exists.
    """

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
