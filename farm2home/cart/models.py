from django.db import models

# Create your models here.

from consumer.models import Consumer

from marketplace.models import Product,BaseClass


class Cart(BaseClass):

    user = models.ForeignKey(Consumer, on_delete=models.CASCADE)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)

    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return f"{self.product.product_name} - {self.user.consumer_name}"
    
    class Meta:

        verbose_name = 'Cart'

        verbose_name_plural = 'Cart'
