from django import forms

from .models import Product , Freshness_choices

class ProductCreationForm(forms.ModelForm):

    class Meta :

        model = Product

        exclude = '__all__'

        widgets ={

                  'farmer_name' : forms.TextInput (attrs={

                                                 'class' : 'form-control',

                                                 'placeholder' : 'Enter Name',

                                                 'required' : 'required'
                                               }),

                   'product_name' : forms.TextInput (attrs={

                                                 'class' : 'form-control',

                                                 'placeholder' : 'Enter Product Name',

                                                 'required' : 'required'
                                               }),

                   'image' : forms.FileInput(attrs={
                                                  
                                                  'class' : 'form-control',                                               
                                                }) ,

                    'price' : forms.NumberInput(attrs={
                                                
                                                  'class' : 'form-control',

                                                  'required' : 'required',

                                                  'placeholder' : 'Enter Price',

                                                 })  , 

                     'quantity' : forms.NumberInput(attrs={
                                                
                                                  'class' : 'form-control',

                                                  'required' : 'required',

                                                  'placeholder' : 'Enter Quantity',

                                                 })  ,   

                      'created_at' : forms.DateTimeField (attrs={
                          
                                                  'class' : 'form-control',

                                                  'required' : 'required'
                          

                      })                                                                                  


                 
        }

        freshness = forms.ChoiceField (choices=Freshness_choices.choices,widget=forms.Select(attrs={
                                                                                     
                                                                                     'class':'form-select',
                                                                                     'required' : 'required'
                                                                                     })) 