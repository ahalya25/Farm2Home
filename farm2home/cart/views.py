from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from consumer.models import Consumer
from marketplace.models import Product
from .models import Cart

# ✅ Add to Cart View
class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, uuid, *args, **kwargs):
        product = get_object_or_404(Product, uuid=uuid)
        profile = request.user
        consumer = get_object_or_404(Consumer, profile=profile)

        cart_item, created = Cart.objects.get_or_create(
            user=consumer,
            product=product,
            defaults={'quantity': 1}
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return redirect('cart-page')  


class CartDetailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        profile = request.user
        consumer = get_object_or_404(Consumer, profile=profile)
        cart_items = Cart.objects.filter(user=consumer)

        # Add a total_price attribute on each cart item
        for item in cart_items:
            item.total_price = item.product.price * item.quantity

        total_price = sum(item.total_price for item in cart_items)

        context = {
            'cart_items': cart_items,
            'total_price': total_price,
        }
        return render(request, 'cart/cart_detail.html', context)

    
class IncreaseQuantityView(LoginRequiredMixin, View):
    def post(self, request, cart_id):
        cart_item = get_object_or_404(Cart, id=cart_id)
        cart_item.quantity += 1
        cart_item.save()
        return redirect('cart-page')

class DecreaseQuantityView(LoginRequiredMixin, View):
    def post(self, request, cart_id):
        cart_item = get_object_or_404(Cart, id=cart_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
        return redirect('cart-page')


