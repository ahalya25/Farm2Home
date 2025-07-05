from django import forms

from .models import Product , Freshness_choices

class ProductAddForm(forms.ModelForm):

    class Meta :

        model = Product

        fields = ['product_name', 'image', 'price', 'offer_price','quantity', 'freshness']

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
      

        freshness = forms.ChoiceField (choices=Freshness_choices.choices,widget=forms.Select(attrs={
                                                                                     
                                                                                     'class':'form-select',
                                                                                     'required' : 'required'
                                                                                     })) 