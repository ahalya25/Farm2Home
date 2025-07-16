from django.contrib import admin

# Register your models here.
from . import models

admin.site.register(models.Cart)

from django.contrib import admin
from .models import Cart

# @admin.register(Cart)
# class CartAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'product', 'quantity')
#     search_fields = ('user__profile__first_name', 'product__product_name')
