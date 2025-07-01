from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser

class RoleChoices(models.TextChoices):

        ADMIN = 'Admin' , 'Admin'

        FARMER = 'Farmer' , 'Farmer'

        CONSUMER = 'Consumer' , 'Consumer'

class Profile(AbstractUser):

        role = models.CharField(max_length=20,choices=RoleChoices.choices)

        def __str__(self):

                return f'{self.name}--{self.last_name}--{self.role}'

        class Meta:

                verbose_name = 'Profile'

                verbose_name_plural = 'Profile'      