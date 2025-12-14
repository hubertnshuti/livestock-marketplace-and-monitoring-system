# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# ------------------------------------
# CORE PROFILE EXTENSION
# ------------------------------------
class UserProfile(models.Model):
    """
    Extends the built-in User model with core fields like role, phone, and picture.
    """
    USER_TYPE_CHOICES = (
        ('farmer', 'Farmer'),
        ('buyer', 'Buyer'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    
    # Contact and Location
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    
    # Optional Fields
    registration_date = models.DateTimeField(default=timezone.now)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='default_profile.png', blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.user_type})"


# ------------------------------------
# ROLE SPECIFIC PROFILES
# ------------------------------------

class Farmer(models.Model):
    """
    Stores farmer-specific data (Farm name, location, etc.).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='farmer_profile')
    farm_name = models.CharField(max_length=255)
    farm_location = models.CharField(max_length=255, blank=True, null=True)
    contact_person = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.farm_name or self.user.username}"


class Buyer(models.Model):
    """
    Stores buyer-specific data (Type, shipping address, etc.).
    """
    BUYER_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('trader', 'Trader'),
        ('butcher', 'Butcher'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='buyer_profile')
    buyer_type = models.CharField(max_length=20, choices=BUYER_TYPE_CHOICES, default='individual')
    shipping_address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.buyer_type})"
    
from django.db import models

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True, null=True)
    subject = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_handled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} from {self.name}"
