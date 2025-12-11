from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Farmer, Buyer

class RegisterForm(forms.ModelForm):
    # Add extra fields that aren't in the default User model
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    
    # User Type Selection (Critical for your app logic)
    USER_TYPE_CHOICES = [
        ('farmer', 'Farmer'),
        ('buyer', 'Buyer'),
    ]
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES, 
        widget=forms.RadioSelect, 
        label="I want to register as a"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        # Validate that passwords match
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")
        
        return cleaned_data

    def save(self, commit=True):
        # Save the User securely
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        
        if commit:
            user.save()
            
            # Create the linked User Profile
            user_type = self.cleaned_data['user_type']
            # Assuming UserProfile has a 'user_type' field based on previous steps
            # If your UserProfile model is different, this might need adjustment, 
            # but this is standard for your description.
            UserProfile.objects.create(user=user, user_type=user_type)
            
            # Create the specific Role Profile (Farmer or Buyer)
            if user_type == 'farmer':
                Farmer.objects.create(user=user)
            elif user_type == 'buyer':
                Buyer.objects.create(user=user)
                
        return user