from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import UserProfile, Farmer, Buyer
from django.contrib.auth.decorators import login_required
from livestock.models import LivestockItem, OrderItem


# ------------------------
# CUSTOM REGISTER FORM
# ------------------------
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    USER_TYPE_CHOICES = [
        ('farmer', 'Farmer'),
        ('buyer', 'Buyer'),
    ]

    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") != cleaned.get("confirm_password"):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned


# ------------------------
# REGISTER VIEW
# ------------------------
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Create User
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            # Create UserProfile (THIS WAS YOUR BUG — MUST BE CREATED)
            user_type = form.cleaned_data["user_type"]
            profile = UserProfile.objects.create(
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
    user = request.user

    # 1. FARMER DASHBOARD LOGIC
    if hasattr(user, 'farmer_profile'):
        # Get all animals belonging to this farmer
        my_livestock = LivestockItem.objects.filter(farmer=user.farmer_profile)
        
        # Count total livestock
        total_livestock = my_livestock.count()
        
        # Find orders related to these animals (where status is pending)
        pending_orders = OrderItem.objects.filter(
            livestock__in=my_livestock, 
            order__order_status='pending_inquiry'
        ).count()
        
        context = {
            'total_livestock': total_livestock,
            'pending_orders': pending_orders, # Pass this count to the template
        }
        return render(request, 'farmer_dashboard.html', context)

    # 2. BUYER DASHBOARD LOGIC
    elif hasattr(user, 'buyer_profile'):
        return render(request, 'buyer_dashboard.html')

    # 3. FALLBACK (Admin or Error)
    else:
        return render(request, 'home.html')