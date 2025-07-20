from django.db import models

# Create your models here.

from consumer.models import BaseClass

class StatusChoices(models.TextChoices):

    PENDING = 'Pending' , 'Pending'

    SUCCESS = 'Success' , 'Success'

    FAILED = 'Failed' , 'Failed'

class Payments(BaseClass):

    consumer = models.ForeignKey('consumer.Consumer',on_delete=models.CASCADE)

    product = models.ForeignKey('marketplace.Product', on_delete=models.CASCADE, null=True, blank=True)

    amount = models.FloatField()

    status = models.CharField(max_length=15,choices=StatusChoices.choices,default=StatusChoices.PENDING)

    paid_at = models.DateTimeField(null=True,blank=True)

    def __str__(self):

        product_name = self.product.product_name if self.product else "Cart"
        return f'{self.consumer.consumer_name}--{product_name}--{self.amount}'

    class Meta :

        verbose_name = 'Payments'

        verbose_name_plural = 'Payments'


class Transactions(BaseClass):

    payment = models.ForeignKey('Payments',on_delete=models.CASCADE)

    rzp_order_id = models.SlugField(null=True,blank=True)

    status = models.CharField(max_length=15, choices=StatusChoices.choices, default=StatusChoices.PENDING)  

    transaction_at = models.DateField(null=True,blank=True)   

    rzp_payment_id = models.SlugField(null=True,blank=True)   

    rzp_payment_signature = models.TextField(null=True,blank=True)

    def __str__(self):
        
        product_name = self.payment.product.product_name if self.payment.product else "Cart"
        return f'{self.payment.consumer.consumer_name}--{product_name}--Transaction'    


    
    class Meta:

        verbose_name = 'Transactions'

        verbose_name_plural = 'Transactions'        



