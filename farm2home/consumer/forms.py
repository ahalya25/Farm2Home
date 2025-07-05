from django import forms

from .models import Consumer

from authentication.models import Profile

class ProfileForm(forms.ModelForm):

    class Meta:

        model = Profile

        # exclude = ['username']

        fields= ['first_name','last_name','email','password','confirm_password']

        widgets= {

            'first_name' : forms.TextInput(attrs={
                                                     'class' : 'form-control',
                                                     'required' : 'required',
                                                      'placeholder': 'Enter first name'}),

            'last_name' : forms.TextInput(attrs={
                                                     'class' : 'form-control',
                                                     'required' : 'required',
                                                      'placeholder': 'Enter last name'}),   

            'email' : forms.EmailInput(attrs={
                                                     'class' : 'form-control',
                                                     'required' : 'required',
                                                      'placeholder': 'Enter valid mail-id'}), 

            'password' : forms.PasswordInput(attrs={
                                                     'class' : 'form-control',
                                                     'required' : 'required'})                                                                                                                                                            

                                                     

            }
        
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
                                                                         'class' : 'form-control',
                                                                         'required' : 'required'}))   
        
    def clean(self):

        validated_data = super().clean()

        print(Profile.objects.values_list('username',flat=True))

        if validated_data.get('email') in Profile.objects.values_list('username',flat=True):

            self.add_error('email','email already taken')


        if validated_data.get('password') != validated_data.get('confirm_password') :

            self.add_error('confirm_password','password mismatch')




class ConsumerForm(forms.ModelForm):

    class Meta:

        model = Consumer

        exclude = ['profile','consumer_name','email','uuid','active_status']

        widgets = {

                
                   'address': forms.Textarea(attrs={
                       
                                                           'class': 'form-control', 
                                                           
                                                           'placeholder': 'Enter your address', 
                                                           
                                                           'rows': 3}),
                 'phone': forms.TextInput(attrs={
                                                           
                                                           'class': 'form-control',
                                                            
                                                           'placeholder': 'Enter 10-digit phone number'})

                                       
        }
