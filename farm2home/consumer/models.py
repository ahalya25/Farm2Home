from django.db import models

# Create your models here.
from marketplace.models import BaseClass  

class Consumer(BaseClass):

    profile = models.OneToOneField('authentication.Profile', on_delete=models.CASCADE)

    consumer_name = models.CharField(max_length=50)

    address = models.TextField()

    phone = models.CharField(max_length=10)

    email = models.EmailField()

    def __str__(self):

        return self.consumer_name
    
    class Meta:

        verbose_name = 'Consumer'

        verbose_name_plural = 'Consumer'
