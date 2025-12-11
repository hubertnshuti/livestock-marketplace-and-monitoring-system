from django.shortcuts import render

# FIX: This corrected import path ensures the views can access the forms 
# defined in the 'accounts' application without causing a ModuleNotFoundError.
# FIX: Changed 'UserRegistrationForm' to 'RegisterForm'
# CORRECT: Import only the forms needed here, using their correct names.
from accounts.forms import RegisterForm, UserUpdateForm, ProfileUpdateForm, FarmerUpdateForm, BuyerUpdateForm 
# ... rest of the file ...
# --- PUBLIC FACING VIEWS (FROM PROJECT ROOT) ---

def home(request):
    # Renders the main index page.
    return render(request, 'home.html')

def for_farmers(request):
    # Renders the landing page marketing to Farmers.
    return render(request, 'for_farmers.html')

def for_buyers(request):
    # Renders the landing page marketing to Buyers.
    return render(request, 'for_buyers.html')

def about(request):
    # Renders the About Us page.
    return render(request, 'about.html')

def contact(request):
    # Renders the Contact Us page.
    return render(request, 'contact.html')

def add_livestock(request):
    # Renders the starting point for the Farmer's livestock listing process.
    return render(request, 'add_livestock.html')