from django import forms

from .models import Product 

class ProductAddForm(forms.ModelForm):

    class Meta :

        model = Product

        exclude = ['farmer','uuid','active_status','freshness']

        # fields = ['product_name', 'image', 'price', 'offer_price','quantity', 'freshness']

        widgets ={

                   'product_name' : forms.TextInput (attrs={

                                                 'class' : 'form-control',

                                                 'placeholder' : 'Enter Product Name',

                                                 'required' : 'required'
                                               }),

                   'image' : forms.FileInput(attrs={
                                                  
                                                  'class' : 'form-control',  
                                                  'required' : 'required '                                            
                                                }) ,

                    'price' : forms.NumberInput(attrs={
                                                
                                                  'class' : 'form-control',

                                                  'required' : 'required',

                                                  'placeholder' : 'Enter Price',

                                                 })  , 

                    'offer_price' : forms.NumberInput(attrs={
                                                
                                                  'class' : 'form-control',

                                                  'placeholder' : 'enter offer price',
                                                        
                                                   }) ,


                     'quantity' : forms.NumberInput(attrs={
                                                
                                                  'class' : 'form-control',

                                                  'required' : 'required',

                                                  'placeholder' : 'Enter Quantity',

                                                 })  
        }                                                                                        
      