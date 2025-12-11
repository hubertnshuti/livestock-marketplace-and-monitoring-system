# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# CORRECT: Import only ACCOUNTS-RELATED forms and models
from .models import UserProfile, Farmer, Buyer
from .forms import (
    RegisterForm, 
    UserUpdateForm, 
    ProfileUpdateForm, 
    FarmerUpdateForm, 
    BuyerUpdateForm
)


# ------------------------
# REGISTER VIEW
# ------------------------
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_type = form.cleaned_data["user_type"]
            
            # Create UserProfile 
            UserProfile.objects.create(
                user=user,
                user_type=user_type
            )

            # Create Farmer or Buyer linked tables
            if user_type == "farmer":
                Farmer.objects.create(
                    user=user,
                    farm_name=f"{user.username}'s Farm"
                )
            else:
                Buyer.objects.create(
                    user=user,
                    buyer_type="individual"
                )

            messages.success(request, f"Registration successful. Welcome!")
            login(request, user)
            return redirect("dashboard")

    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


# ------------------------
# LOGIN VIEW
# ------------------------
def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            login(request, form.get_user())
            return redirect("dashboard")

    return render(request, "login.html", {"form": form})


# ------------------------
# DASHBOARD VIEW
# ------------------------
@login_required
def dashboard(request):
    user_profile = request.user.userprofile 

    if user_profile.user_type == "farmer":
        farmer = getattr(request.user, 'farmer_profile', None) 
        
        context = {
            "profile": user_profile,
            # Placeholder for future dashboard data
        }
        return render(request, "farmer_dashboard.html", context)

    elif user_profile.user_type == "buyer":
        buyer = getattr(request.user, 'buyer_profile', None) 
        
        context = {
            "profile": user_profile,
            # Placeholder for future dashboard data
        }
        return render(request, "buyer_dashboard.html", context)

    return render(request, "dashboard.html", {"profile": user_profile})


# ------------------------
# PROFILE VIEW
# ------------------------
@login_required
def profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    farmer_form = None
    buyer_form = None

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        
        # Handle Role Specifics
        if hasattr(request.user, 'farmer_profile'):
            farmer_form = FarmerUpdateForm(request.POST, instance=request.user.farmer_profile)
        elif hasattr(request.user, 'buyer_profile'):
            buyer_form = BuyerUpdateForm(request.POST, instance=request.user.buyer_profile)

        # Validation Check
        if u_form.is_valid() and p_form.is_valid():
            role_valid = True
            if farmer_form and not farmer_form.is_valid(): role_valid = False
            if buyer_form and not buyer_form.is_valid(): role_valid = False
            
            if role_valid:
                u_form.save()
                p_form.save()
                if farmer_form: farmer_form.save()
                if buyer_form: buyer_form.save()
                
                messages.success(request, f'Your account has been updated!')
                return redirect('profile')
        else:
            messages.error(request, 'Error updating profile. Please check the fields.')

    else:
        # GET Request - Pre-fill forms with current data
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=user_profile)
        
        if hasattr(request.user, 'farmer_profile'):
            farmer_form = FarmerUpdateForm(instance=request.user.farmer_profile)
        elif hasattr(request.user, 'buyer_profile'):
            buyer_form = BuyerUpdateForm(instance=request.user.buyer_profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'farmer_form': farmer_form,
        'buyer_form': buyer_form,
        'is_farmer': user_profile.user_type == 'farmer'
    }

    return render(request, 'profile.html', context)