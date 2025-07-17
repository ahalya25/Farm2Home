# # rating/forms.py
# from django import forms
# from .models import ProductReview

# class ProductReviewForm(forms.ModelForm):
#     class Meta:
#         model = ProductReview
#         fields = ['rating', 'comment']
#         widgets = {
#             'rating': forms.RadioSelect(choices=[(i, f"{i} ★") for i in range(1, 6)]),

#             'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add your review...'}),
#         }
