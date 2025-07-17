# from django.db import models
# from django.conf import settings
# from marketplace.models import Product , BaseClass # Import the Product model

# class ProductReview(BaseClass):

#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')

#     consumer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

#     rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])

#     comment = models.TextField()

#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:

#         unique_together = ('product', 'consumer')

#     def __str__(self):
        
#         return f'{self.consumer.username} - {self.product.name} ({self.rating})'
