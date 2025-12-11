import requests
import uuid
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LivestockItemForm, LivestockImageForm, SimpleOrderForm
from .models import LivestockItem, LivestockImage, Order, OrderItem

# 1. CREATE BASIC INFO
@login_required
def livestock_create(request):
    if request.method == 'POST':
        form = LivestockItemForm(request.POST)
        if form.is_valid():
            livestock_item = form.save(commit=False)
            if hasattr(request.user, 'farmer_profile'):
                livestock_item.farmer = request.user.farmer_profile
                livestock_item.save()
                return redirect('livestock:add_photos', pk=livestock_item.pk)
            else:
                messages.error(request, "You must be a registered farmer to list livestock.")
                return redirect('dashboard')
    else:
        form = LivestockItemForm()
        
    return render(request, 'add_livestock.html', {'form': form})

# 2. ADD PHOTOS VIEW
@login_required
def add_photos(request, pk):
    livestock = get_object_or_404(LivestockItem, pk=pk, farmer=request.user.farmer_profile)
    
    if request.method == 'POST':
        form = LivestockImageForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.livestock = livestock
            photo.save()
            messages.success(request, "Photo uploaded successfully!")
            return redirect('livestock:add_photos', pk=pk) 
    else:
        form = LivestockImageForm()

    photos = livestock.images.all()

    return render(request, 'add_photos.html', {
        'form': form, 
        'livestock': livestock, 
        'photos': photos
    })

# 3. SUCCESS VIEW
@login_required
def upload_success(request):
    return render(request, 'upload_success.html')

# 4. MARKETPLACE VIEW
def marketplace(request):
    listings = LivestockItem.objects.filter(is_for_sale=True, status='available').order_by('-listing_date')
    context = {
        'listings': listings,
        'page_title': 'Marketplace'
    }
    return render(request, 'marketplace.html', context)

# 5. DETAIL VIEW
def livestock_detail(request, pk):
    livestock = get_object_or_404(LivestockItem, pk=pk)
    photos = livestock.images.all()
    context = {
        'livestock': livestock,
        'photos': photos,
        'page_title': f"{livestock.species.species_name} Details"
    }
    return render(request, 'livestock_detail.html', context)

# 6. PLACE ORDER VIEW (With Duplicate Check)
@login_required
def place_order(request, pk):
    if not hasattr(request.user, 'buyer_profile'):
        messages.error(request, "Only registered buyers can place orders.")
        return redirect('dashboard')
        
    livestock_item = get_object_or_404(LivestockItem, pk=pk)
    buyer = request.user.buyer_profile

    # Availability Check
    if not livestock_item.is_for_sale or livestock_item.status != 'available':
        messages.error(request, "This item has already been sold.")
        return redirect('livestock:marketplace')

    # Duplicate Check
    existing_order = Order.objects.filter(
        buyer=buyer, 
        payment_status='pending',
        order_items__livestock=livestock_item
    ).first()

    if existing_order:
        messages.info(request, "You already have a pending order for this item. Resuming payment...")
        return redirect('livestock:retry_payment', pk=existing_order.pk)

    if request.method == 'POST':
        form = SimpleOrderForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            amount = livestock_item.price * quantity
            tx_ref = str(uuid.uuid4())
            
            new_order = Order.objects.create(
                buyer=buyer,
                total_amount=amount,
                order_status='pending_payment',
                payment_status='pending',
            )
            
            OrderItem.objects.create(
                order=new_order,
                livestock=livestock_item,
                quantity=quantity,
                unit_price_at_time=livestock_item.price,
            )

            context = {
                'order': new_order,
                'item': livestock_item,
                'tx_ref': tx_ref
            }
            return render(request, 'payment_simulation.html', context)
            
    return redirect('livestock:livestock_detail', pk=pk)

# 7. PAYMENT CALLBACK
@login_required
def payment_callback(request):
    tx_ref = request.GET.get('tx_ref')
    fake_status = request.GET.get('status') 

    if fake_status == 'success':
        order = Order.objects.filter(buyer=request.user.buyer_profile, payment_status='pending').last()
        
        if order:
            order.payment_status = 'paid'
            order.order_status = 'confirmed'
            order.save()
            
            # Use direct lookup to fix naming error
            items = OrderItem.objects.filter(order=order)
            for item in items:
                item.livestock.status = 'sold'
                item.livestock.is_for_sale = False
                item.livestock.save()
                
            messages.success(request, f"Payment Successful! Order #{order.order_id} confirmed.")
            return redirect('livestock:order_history')
            
    messages.error(request, "Payment failed or cancelled.")
    return redirect('dashboard')

# 8. BUYER ORDER HISTORY
@login_required
def order_history(request):
    if not hasattr(request.user, 'buyer_profile'):
        messages.error(request, "You are not registered as a buyer.")
        return redirect('dashboard')
        
    buyer_orders = Order.objects.filter(buyer=request.user.buyer_profile).order_by('-order_date')
    
    context = {
        'orders': buyer_orders,
        'page_title': 'My Order History'
    }
    return render(request, 'buyer_order_history.html', context)

# 9. FARMER SALES INQUIRIES
@login_required
def sales_inquiries(request):
    if not hasattr(request.user, 'farmer_profile'):
        messages.error(request, "You are not registered as a farmer.")
        return redirect('dashboard')
    
    farmer_items = LivestockItem.objects.filter(farmer=request.user.farmer_profile)
    sales_inquiries = OrderItem.objects.filter(livestock__in=farmer_items).select_related('order', 'livestock')
    
    context = {
        'inquiries': sales_inquiries,
        'page_title': 'Incoming Sales Inquiries'
    }
    return render(request, 'farmer_sales_inquiries.html', context)

# 10. APPROVE INQUIRY
@login_required
def approve_inquiry(request, pk):
    inquiry_item = get_object_or_404(OrderItem, pk=pk)
    
    if inquiry_item.livestock.farmer != request.user.farmer_profile:
        messages.error(request, "You do not have permission to manage this order.")
        return redirect('livestock:sales_inquiries')

    order = inquiry_item.order
    order.order_status = 'confirmed'
    order.save()

    animal = inquiry_item.livestock
    animal.status = 'sold'
    animal.is_for_sale = False
    animal.save()

    messages.success(request, f"Sale confirmed! {animal.species.species_name} marked as SOLD.")
    return redirect('livestock:sales_inquiries')

# 11. REJECT INQUIRY
@login_required
def reject_inquiry(request, pk):
    inquiry_item = get_object_or_404(OrderItem, pk=pk)
    
    if inquiry_item.livestock.farmer != request.user.farmer_profile:
        messages.error(request, "Permission denied.")
        return redirect('livestock:sales_inquiries')

    order = inquiry_item.order
    order.order_status = 'cancelled'
    order.save()
    
    messages.info(request, "Inquiry rejected. The animal remains available.")
    return redirect('livestock:sales_inquiries')

# 12. RETRY PAYMENT (Smart Version)
@login_required
def retry_payment(request, pk):
    order = get_object_or_404(Order, pk=pk, buyer=request.user.buyer_profile)
    
    if order.payment_status == 'paid':
        messages.info(request, "This order is already paid.")
        return redirect('livestock:order_history')
        
    order_item = OrderItem.objects.filter(order=order).first()
    if not order_item:
        messages.error(request, "Order has no items.")
        return redirect('livestock:order_history')
        
    livestock_item = order_item.livestock
    
    # Check if sold to someone else
    if livestock_item.status == 'sold':
        # If sold, BUT this order is the one that is 'Confirmed' (Farmer Accepted), allow pay.
        if order.order_status == 'confirmed':
            pass 
        else:
            order.order_status = 'cancelled'
            order.save()
            messages.error(request, "Sorry, this item was sold to another buyer.")
            return redirect('livestock:order_history')
    
    tx_ref = str(uuid.uuid4())
    context = {
        'order': order,
        'item': livestock_item, 
        'tx_ref': tx_ref
    }
    return render(request, 'payment_simulation.html', context)