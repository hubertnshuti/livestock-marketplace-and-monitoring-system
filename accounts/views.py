from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from .models import UserProfile
# IMPORT LIVESTOCK MODELS to fetch data
from livestock.models import LivestockItem, Order, OrderItem 
from django.db.models import Sum

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})

@login_required
def dashboard(request):
    profile = request.user.profile

    # --- LOGIC FOR FARMERS ---
    if profile.user_type == "farmer":
        farmer = request.user.farmer_profile
        
        # 1. My Livestock Stats
        total_livestock = farmer.livestock_items.count()
        recent_listings = farmer.livestock_items.all().order_by('-listing_date')[:5]
        
        # 2. Incoming Orders (Sales)
        # Get items owned by this farmer
        my_items = farmer.livestock_items.all()
        # Find OrderItems that reference these items
        incoming_sales = OrderItem.objects.filter(livestock__in=my_items).select_related('order')
        
        # Count pending sales
        active_alerts = incoming_sales.filter(order__order_status='pending_inquiry').count()
        
        # Calculate Sold count (items marked as sold)
        sold_count = my_items.filter(status='sold').count()

        context = {
            "profile": profile,
            "total_livestock": total_livestock,
            "recent_listings": recent_listings,
            "active_alerts": active_alerts, # Pending Orders count
            "sold_count": sold_count,
            "incoming_sales": incoming_sales[:5] # Show last 5 inquiries
        }
        return render(request, "farmer_dashboard.html", context)

    # --- LOGIC FOR BUYERS ---
    elif profile.user_type == "buyer":
        buyer = request.user.buyer_profile
        
        # 1. Fetch Orders placed by this buyer
        my_orders = Order.objects.filter(buyer=buyer).order_by('-order_date')
        
        # 2. Stats
        active_orders_count = my_orders.exclude(order_status='completed').count()
        
        # Calculate Total Spent (Sum of total_amount)
        total_spent = my_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        context = {
            "profile": profile,
            "orders": my_orders[:5], # Recent 5 orders
            "active_orders_count": active_orders_count,
            "total_spent": total_spent,
            "saved_items_count": 0 # Placeholder for wishlist
        }
        return render(request, "buyer_dashboard.html", context)

    return render(request, "dashboard.html", {"profile": profile})