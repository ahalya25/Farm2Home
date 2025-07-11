from django import forms

from .models import Farmer

class FarmerForm(forms.ModelForm):

    class Meta:

        model = Farmer

        exclude = ['profile','farmer_name','uuid','active_status']  

        widgets = {


            
            'image': forms.FileInput(attrs={
                
                                                     'class': 'form-control'}),

            'location': forms.TextInput(attrs={

                                                     'class': 'form-control', 

                                                    'placeholder': 'Enter location'}),

            'phone': forms.TextInput(attrs={

                                                     'class': 'form-control',

                                                     'placeholder': 'Enter phone number'})

            
        }