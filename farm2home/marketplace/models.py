from django.db import models

# Create your models here.
import uuid

class BaseClass(models.Model):

    uuid = models.SlugField(unique=True,default=uuid.uuid4)

    active_status = models.BooleanField(default=True)

    created_at =  models.DateTimeField(auto_now_add=True)

    updated_at =  models.DateTimeField(auto_now=True)

    class Meta: # set for abstract class

        abstract = True


class Freshness_choices(models.TextChoices):

    FRESH = 'Fresh', 'Fresh',
                         
    MEDIUM = 'Medium', 'Medium',

    SPOILED = 'Spoiled', 'Spoiled'     

class Product(BaseClass):

    farmer_name = models.ForeignKey('farmer.Farmer',on_delete=models.CASCADE)

    product_name = models.CharField(max_length=100)

    image = models.ImageField(upload_to='products/')

    price = models.DecimalField(max_digits=6, decimal_places=2)

    quantity = models.PositiveIntegerField()

    freshness = models.CharField(max_length=20, choices=Freshness_choices)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return f"{self.product_name} - {self.freshness}"
    
    class Meta:

        verbose_name = 'Product'

        verbose_name_plural = 'Product'
