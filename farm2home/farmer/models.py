from django.db import models

# Create your models here.
from marketplace.models import BaseClass

class Farmer(BaseClass):

    profile = models.OneToOneField('authentication.Profile',on_delete=models.CASCADE)

    farmer_name = models.CharField(max_length=50)

    image =  models.ImageField(upload_to='farmer-images/')

    location = models.CharField(max_length=30)

    phone = models.CharField(max_length=10)

    def __str__(self):

        return self.farmer_name
    
    class Meta:

        verbose_name = 'Farmer'

        verbose_name_plural = 'Farmer'