# ai_quality/forms.py

from django import forms

class QualityCheckForm(forms.Form):
    image = forms.ImageField()
