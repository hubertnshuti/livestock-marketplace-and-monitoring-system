# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .forms import (
    UserRegistrationForm,
    LoginForm,
    UserProfileForm,          
    UserProfileUpdateForm,
    FarmerProfileUpdateForm,
    BuyerProfileUpdateForm,
    ContactForm
)
from .models import UserProfile, Farmer, Buyer, ContactMessage

# FIX: Import OrderItem and Order so they can be used in the dashboard logic
from livestock.models import LivestockItem, OrderItem, Order


# --- 1. REGISTRATION VIEW ---
def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, "Registration successful!")
                
                # Route based on user type
                if hasattr(user, 'farmer_profile'):
                    messages.info(request, "Welcome to your Farm Dashboard!")
                    return redirect('dashboard')
                else:
                    messages.info(request, "Welcome to the Marketplace!")
                    return redirect('livestock:marketplace')
            except Exception as e:
                messages.error(request, f"Registration error: {e}")
                return redirect('register')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

# --- 2. LOGIN VIEW ---
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # ATTRACTION LOGIC: Buyers go straight to Marketplace
            try:
                if user.userprofile.user_type == 'farmer':
                    return redirect('dashboard')
                else:
                    return redirect('livestock:marketplace')
            except:
                # Fallback for admins/users without profile
                return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

# --- 3. LOGOUT VIEW ---
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    user = request.user
   
    # 1. Get the profile securely
    try:
        profile = user.userprofile
    except:
        # Graceful fallback if profile doesn't exist
        profile = None
    
    context = {'profile': profile}

    # --- LOGIC FOR FARMERS ---
    if profile and profile.user_type == 'farmer':
        try:
            # Get all items owned by this farmer
            farmer_items = LivestockItem.objects.filter(farmer=user.farmer_profile)
            
            # 1. Total Livestock: Exclude 'sold' items as requested
            context['total_livestock'] = farmer_items.exclude(status='sold').count()
            
            # 2. Sold Count: Count only 'sold' items
            context['sold_count'] = farmer_items.filter(status='sold').count()
            
            # 3. Reserved Count: Count items currently in negotiation/delivery
            context['reserved_count'] = farmer_items.filter(status='reserved').count()

            # 4. Recent Listings: For the table
            context['recent_listings'] = farmer_items.order_by('-listing_date')[:5]
            
            # 5. Inquiries: Find order items related to this farmer's livestock
            inquiries = OrderItem.objects.filter(livestock__in=farmer_items)
            
            # 6. New Inquiries Count: Only count orders with status 'inquiry_sent'
            # This matches the {{ new_inquiries_count }} variable in your template
            context['new_inquiries_count'] = inquiries.filter(order__order_status='inquiry_sent').count()
            
            # 7. Incoming Sales list (optional, if used in sidebar or extra widgets)
            context['incoming_sales'] = inquiries.order_by('-order__order_date')[:5]
           
        except Exception as e:
            print(f"Dashboard Error: {e}")
            context['total_livestock'] = 0
            context['new_inquiries_count'] = 0
            context['reserved_count'] = 0
           
        return render(request, 'farmer_dashboard.html', context)

    # --- LOGIC FOR BUYERS ---
    elif profile and profile.user_type == 'buyer':
        try:
            buyer_orders = Order.objects.filter(buyer=user.buyer_profile)
           
            # Count active orders (Inquiry Sent or Approved)
            # We exclude 'pending' (cart) and 'confirmed' (completed history)
            active_orders = buyer_orders.filter(order_status__in=['inquiry_sent', 'approved']).count()
           
            # Calculate total spent (only where payment is strictly 'paid')
            total_spent = buyer_orders.filter(payment_status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
           
            context['active_orders_count'] = active_orders
            context['total_spent'] = total_spent
            context['orders'] = buyer_orders.order_by('-order_date')[:5] # Show recent 5 orders
           
        except Exception as e:
            print(f"Buyer Dashboard Error: {e}")
            context['active_orders_count'] = 0
            context['total_spent'] = 0
            
        return render(request, 'buyer_dashboard.html', context)

    # --- FALLBACK ---
    messages.error(request, "Profile not found. Please contact support.")
    return redirect('home')

# --- 5. PROFILE VIEW ---
@login_required
def profile(request):
    user = request.user

    # Get or create base profile
    try:
        profile_instance = user.userprofile
    except UserProfile.DoesNotExist:
        profile_instance = UserProfile.objects.create(
            user=user,
            user_type="buyer",  # default if somehow missing
        )

    # Prepare role-specific instance (farmer or buyer)
    farmer_instance = None
    buyer_instance = None

    if profile_instance.user_type == "farmer":
        farmer_instance, _ = Farmer.objects.get_or_create(user=user, defaults={
            "farm_name": user.username,
        })
    elif profile_instance.user_type == "buyer":
        buyer_instance, _ = Buyer.objects.get_or_create(user=user)

    if request.method == "POST":
        profile_form = UserProfileUpdateForm(
            request.POST, request.FILES, instance=profile_instance
        )

        farmer_form = None
        buyer_form = None

        if profile_instance.user_type == "farmer" and farmer_instance:
            farmer_form = FarmerProfileUpdateForm(
                request.POST, instance=farmer_instance
            )
        elif profile_instance.user_type == "buyer" and buyer_instance:
            buyer_form = BuyerProfileUpdateForm(
                request.POST, instance=buyer_instance
            )

        # Validate both forms that exist
        forms_valid = profile_form.is_valid()
        if farmer_form is not None:
            forms_valid = forms_valid and farmer_form.is_valid()
        if buyer_form is not None:
            forms_valid = forms_valid and buyer_form.is_valid()

        if forms_valid:
            profile_form.save()
            if farmer_form is not None:
                farmer_form.save()
            if buyer_form is not None:
                buyer_form.save()

            messages.success(request, "Profile updated successfully.")
            return redirect("profile")
    else:
        profile_form = UserProfileUpdateForm(instance=profile_instance)
        farmer_form = None
        buyer_form = None

        if profile_instance.user_type == "farmer" and farmer_instance:
            farmer_form = FarmerProfileUpdateForm(instance=farmer_instance)
        elif profile_instance.user_type == "buyer" and buyer_instance:
            buyer_form = BuyerProfileUpdateForm(instance=buyer_instance)

    context = {
        "profile_form": profile_form,
        "farmer_form": farmer_form,
        "buyer_form": buyer_form,
        "profile": profile_instance,
    }
    return render(request, "profile.html", context)

# --- 6. CONTACT VIEW ---
def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  # saves ContactMessage in DB
            messages.success(request, "Thank you. Your message has been sent.")
            return redirect("contact")
    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form})



def disclaimer_view(request):
    return render(request, "disclaimer.html")

def privacy_policy_view(request):
    return render(request, "privacy_policy.html")

def terms_of_use_view(request):
    return render(request, "terms_of_use.html")


