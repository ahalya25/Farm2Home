from django import forms

from .models import Consumer

class ConsumerForm(forms.ModelForm):

    class Meta:

        model = Consumer

        fields = '__all__'

        widgets = {

                  'consumer_name': forms.TextInput(attrs={
                      
                                                           'class': 'form-control',
                                                            
                                                             'placeholder': 'Enter your name'}),
                   'address': forms.Textarea(attrs={
                       
                                                           'class': 'form-control', 
                                                           
                                                           'placeholder': 'Enter your address', 
                                                           
                                                           'rows': 3}),
                 'phone': forms.TextInput(attrs={
                                                           
                                                           'class': 'form-control',
                                                            
                                                           'placeholder': 'Enter 10-digit phone number'}),

                 'email': forms.EmailInput(attrs={
                     
                                                          'class': 'form-control',
                                                           
                                                         'placeholder': 'Enter your email'}),
        }
