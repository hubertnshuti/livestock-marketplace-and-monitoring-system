# accounts/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Farmer, Buyer # Only account-related models here


# --- 1. REGISTRATION FORM (Used by register_view) ---
class RegisterForm(forms.ModelForm):
    # This correctly accesses the choices defined inside the UserProfile model class
    user_type = forms.ChoiceField(choices=UserProfile.USER_TYPE_CHOICES) 
    
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label='Confirm Password')

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name"]

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") != cleaned.get("confirm_password"):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


# --- 2. UPDATE FORMS (Used by profile view) ---
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'location', 'profile_picture']

class FarmerUpdateForm(forms.ModelForm):
    class Meta:
        model = Farmer
        fields = ['farm_name', 'farm_location']

class BuyerUpdateForm(forms.ModelForm):
    class Meta:
        model = Buyer
        fields = ['shipping_address']