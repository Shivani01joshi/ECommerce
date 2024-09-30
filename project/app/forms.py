import random
import string
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Category, Product, Rating, Shipment, checkoutAddress

class CustomUserCreationForm(UserCreationForm):
    
    email = forms.EmailField(
        required=True,
        help_text='Required. Enter a valid email address.',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with that email already exists.')
        return email

class ForgetPasswordForm(forms.Form):
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address')

class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(required=True, widget=forms.PasswordInput)
    password2 = forms.CharField(required=True, widget=forms.PasswordInput)

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'review': forms.Textarea(attrs={'rows': 4}),
        }

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = checkoutAddress
        fields = '__all__'

class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100)

class ShipmentForm(forms.ModelForm):
    length = forms.DecimalField(max_digits=10, decimal_places=2, label="Length (cm)")
    breadth = forms.DecimalField(max_digits=10, decimal_places=2, label="Breadth (cm)")
    weight = forms.DecimalField(max_digits=10, decimal_places=2, label="Weight (kg)")
    tracking_number = forms.CharField(max_length=100, label="Tracking Number")
    shipment_status = forms.ChoiceField(choices=[('Pending', 'Pending'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered')])
    edd = forms.DateTimeField(label="Estimated Delivery Date")

    class Meta:
        model = Shipment
        fields = ['tracking_number','shipment_status', 'edd']  # Add 'tracking_number' if you want it in the form

    
    def save(self, order=None, commit=True):
        shipment = super().save(commit=False)
        if order:
            shipment.order = order  # Assigning the order to the shipment
        shipment.dimensions = f"Length: {self.cleaned_data['length']} cm, Breadth: {self.cleaned_data['breadth']} cm, Weight: {self.cleaned_data['weight']} kg"
        if commit:
            shipment.save()
        return shipment