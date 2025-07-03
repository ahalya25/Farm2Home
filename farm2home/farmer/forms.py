from django import forms

from .models import Farmer

class FarmerForm(forms.ModelForm):

    class Meta:

        model = Farmer

        fields = '__all__'

        widgets = {

            'farmer_name': forms.TextInput(attrs={
                                                    'class': 'form-control', 
                                                    
                                                     'placeholder': 'Enter your name'}),

            'image': forms.FileInput(attrs={
                
                                                     'class': 'form-control'}),

            'location': forms.TextInput(attrs={

                                                     'class': 'form-control', 

                                                    'placeholder': 'Enter location'}),

            'phone': forms.TextInput(attrs={

                                                     'class': 'form-control',

                                                     'placeholder': 'Enter phone number'}),

            'profile': forms.Select(attrs={

                                                     'class': 'form-control'}),
        }
