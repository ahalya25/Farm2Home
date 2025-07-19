from django.db import models
from django.conf import settings
from marketplace.models import Product , BaseClass
from datetime import timedelta, date

class Orders(BaseClass):

    status_choices = [
        ('ordered', 'Ordered'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]

    consumer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)

    status = models.CharField(max_length=20, choices=status_choices, default='ordered')

    ordered_at = models.DateTimeField(auto_now_add=True)

    expected_delivery = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):

        if not self.expected_delivery:

            self.expected_delivery = date.today() + timedelta(days=5)  # 5 days by default

        super().save(*args, **kwargs)

    def __str__(self):

        return f"{self.product.product_name} - {self.consumer}"
    
    class Meta:

        verbose_name = 'Orders'

        verbose_name_plural = 'Orders'
