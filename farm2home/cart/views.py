# cart/views.py
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from consumer.models import Consumer
from marketplace.models import Product
from .models import Cart

class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, uuid, *args, **kwargs):
        # ✅ Get the product by UUID
        product = get_object_or_404(Product, uuid=uuid)

        # ✅ Get the logged-in user's profile
        profile = request.user.profile  # ✅ Correct


        # ✅ Get the Consumer related to this profile
        consumer = get_object_or_404(Consumer, profile=profile)

        # ✅ Add or update the cart item
        cart_item, created = Cart.objects.get_or_create(user=consumer, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return redirect('cart')  # Or redirect to 'product-list' etc.
