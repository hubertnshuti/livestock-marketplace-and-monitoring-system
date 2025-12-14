import re  # <--- Added for password complexity checks
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import UserProfile, Farmer, Buyer, ContactMessage


# --- 1. REGISTRATION FORM ---
class UserRegistrationForm(forms.ModelForm):
    # 1. Standard User Fields
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create a password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}), label="Confirm Password")
    
    # 2. Profile Fields
    phone_number = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 078 000 0000'}))
    location = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Musanze, Northern Province'}))
    
    # 3. Farmer Specific Fields
    farm_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Green Valley Farm'}))
    farm_location = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Kimironko, Kigali'}))
    contact_person = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. John Doe'}))

    # 4. User Type Selector
    USER_TYPE_CHOICES = [('farmer', 'Farmer'), ('buyer', 'Buyer')]
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, widget=forms.RadioSelect, label="I want to join as a")


    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
        }


    # --- NEW: Email Uniqueness Check ---
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email


    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        user_type = cleaned_data.get("user_type")
        farm_name = cleaned_data.get("farm_name")
        farm_location = cleaned_data.get("farm_location")
        contact_person = cleaned_data.get("contact_person")


        # --- NEW: Password Complexity Checks ---
        if password:
            # Check length
            if len(password) < 8:
                self.add_error('password', "Password must be at least 8 characters long.")
            
            # Check for digit
            if not re.search(r'\d', password):
                self.add_error('password', "Password must contain at least one number (0-9).")
            
            # Check for letter
            if not re.search(r'[a-zA-Z]', password):
                self.add_error('password', "Password must contain at least one letter.")
            
            # Check for special character
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                self.add_error('password', "Password must contain at least one special character (@, #, $, etc).")


        # Password Match Check
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")
        
        # Farmer Requirement Check
        if user_type == 'farmer':
            if not farm_name:
                self.add_error('farm_name', "Farm Name is required for farmers.")
            if not farm_location:
                self.add_error('farm_location', "Farm Location is required for farmers.")
            if not contact_person:
                self.add_error('contact_person', "Contact Person is required for farmers.")
        
        return cleaned_data


    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        
        if commit:
            user.save()
            
            user_type = self.cleaned_data['user_type']
            
            # Create UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user, defaults={
                'user_type': user_type,
                'phone_number': self.cleaned_data['phone_number'],
                'location': self.cleaned_data['location']
            })
            
            # Update if it existed (edge case fix)
            if not created:
                profile.user_type = user_type
                profile.phone_number = self.cleaned_data['phone_number']
                profile.location = self.cleaned_data['location']
                profile.save()
            
            # Create Farmer or Buyer specific tables
            if user_type == 'farmer':
                Farmer.objects.create(
                    user=user,
                    farm_name=self.cleaned_data['farm_name'],
                    farm_location=self.cleaned_data['farm_location'],
                    contact_person=self.cleaned_data['contact_person']
                )
            elif user_type == 'buyer':
                Buyer.objects.create(user=user)
                    
        return user



# --- 2. LOGIN FORM ---
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


# --- 3. PROFILE FORM ---
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'phone_number', 'location']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }
        
        
class UserProfileUpdateForm(forms.ModelForm):
    """General fields that both farmers and buyers can edit."""
    class Meta:
        model = UserProfile
        fields = ["profile_picture", "phone_number", "location"]
        widgets = {
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
        }


class FarmerProfileUpdateForm(forms.ModelForm):
    """Farmer‑specific fields."""
    class Meta:
        model = Farmer
        fields = ["farm_name", "farm_location", "contact_person"]
        widgets = {
            "farm_name": forms.TextInput(attrs={"class": "form-control"}),
            "farm_location": forms.TextInput(attrs={"class": "form-control"}),
            "contact_person": forms.TextInput(attrs={"class": "form-control"}),
        }


class BuyerProfileUpdateForm(forms.ModelForm):
    """Buyer‑specific fields."""
    class Meta:
        model = Buyer
        fields = ["buyer_type", "shipping_address"]
        widgets = {
            "buyer_type": forms.Select(attrs={"class": "form-select"}),
            "shipping_address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "subject": forms.TextInput(attrs={"class": "form-control"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }