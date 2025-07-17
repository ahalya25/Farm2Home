# # rating/views.py
# from django.views import View
# from django.shortcuts import render, redirect, get_object_or_404
# from marketplace.models import Product
# from .models import ProductReview
# from .forms import ProductReviewForm
# from django.contrib.auth.decorators import login_required
# from django.utils.decorators import method_decorator

# @method_decorator(login_required, name='dispatch')
# class AddReviewView(View):
#     def get(self, request, product_id):
#         product = get_object_or_404(Product, id=product_id)
#         form = ProductReviewForm()
#         return render(request, 'rating/add_review.html', {'form': form, 'product': product})

#     def post(self, request, product_id):
#         product = get_object_or_404(Product, id=product_id)
#         form = ProductReviewForm(request.POST)
#         if form.is_valid():
#             review = form.save(commit=False)
#             review.product = product
#             review.consumer = request.user
#             review.save()
#             return redirect('product-detail', pk=product.id)
#         return render(request, 'rating/add_review.html', {'form': form, 'product': product})
