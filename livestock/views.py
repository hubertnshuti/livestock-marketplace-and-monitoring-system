# livestock/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q # Needed later for filtering

# FIX: Import the forms from the local livestock/forms.py file
from .forms import LivestockItemForm, LivestockImageForm, SimpleOrderForm 
from .models import LivestockItem, LivestockImage, Order, OrderItem
# Note: Species/Breed models are loaded via forms now


# --- 1. CREATE BASIC INFO (Step 1) ---
@login_required
def livestock_create(request):
    if request.method == 'POST':
        form = LivestockItemForm(request.POST)
        if form.is_valid():
            livestock_item = form.save(commit=False)
            
            if hasattr(request.user, 'farmer_profile'):
                livestock_item.farmer = request.user.farmer_profile
                livestock_item.save()
                messages.success(request, "Basic information saved. Now add photos.")
                # Redirect to the photo upload page (Step 2)
                return redirect('livestock:add_photos', pk=livestock_item.pk)
            else:
                messages.error(request, "You must be a registered farmer to list livestock.")
                return redirect('dashboard')
    else:
        form = LivestockItemForm()
        
    return render(request, 'add_livestock.html', {'form': form})

# --- 2. ADD PHOTOS VIEW (Step 2) ---
@login_required
def add_photos(request, pk):
    # This view requires a template named add_photos.html
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

# --- 3. SUCCESS VIEW (Step 3) ---
@login_required
def upload_success(request):
    return render(request, 'upload_success.html')

# --- 4. MARKETPLACE VIEW (For Buyers) ---
def marketplace(request):
    listings = LivestockItem.objects.filter(is_for_sale=True, status='available').order_by('-listing_date')
    
    context = {
        'listings': listings,
        'page_title': 'Marketplace'
    }
    return render(request, 'marketplace.html', context)
    
# --- 5. DETAIL PAGE VIEW ---
def livestock_detail(request, pk):
    livestock = get_object_or_404(LivestockItem, pk=pk)
    order_form = SimpleOrderForm()
    
    context = {
        'livestock': livestock,
        'order_form': order_form,
        'photos': livestock.images.all()
    }
    return render(request, 'livestock_detail.html', context)

# --- 6. ORDER PLACEMENT VIEW (Buy Now Logic) ---
@login_required
def place_order(request, pk):
    if not hasattr(request.user, 'buyer_profile'):
        messages.error(request, "Only registered buyers can place orders.")
        return redirect('dashboard')
        
    livestock_item = get_object_or_404(LivestockItem, pk=pk)
    buyer = request.user.buyer_profile

    if livestock_item.is_for_sale == False or livestock_item.status != 'available':
        messages.error(request, "This item is not currently available for purchase.")
        return redirect('livestock:livestock_detail', pk=pk)

    if request.method == 'POST':
        form = SimpleOrderForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            
            # 1. CREATE the Order header
            new_order = Order.objects.create(
                buyer=buyer,
                total_amount=livestock_item.price * quantity,
                order_status='pending_inquiry',
                payment_status='pending'
            )
            
            # 2. CREATE the OrderItem line
            OrderItem.objects.create(
                order=new_order,
                livestock=livestock_item,
                quantity=quantity,
                unit_price_at_time=livestock_item.price,
            )

            messages.success(request, f"Your inquiry for {livestock_item.species.species_name} has been sent. Order #{new_order.pk} logged.")
            return redirect('dashboard') 
            
    return redirect('livestock:livestock_detail', pk=pk)

# --- 7. BUYER ORDER HISTORY ---
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

# --- 8. FARMER SALES INQUIRIES ---
@login_required
def sales_inquiries(request):
    if not hasattr(request.user, 'farmer_profile'):
        messages.error(request, "You are not registered as a farmer.")
        return redirect('dashboard')
    
    farmer_items = LivestockItem.objects.filter(farmer=request.user.farmer_profile)
    sales_inquiries = OrderItem.objects.filter(livestock__in=farmer_items).select_related('order', 'livestock').order_by('-order__order_date')
    
    context = {
        'inquiries': sales_inquiries,
        'page_title': 'Incoming Sales Inquiries'
    }
    return render(request, 'farmer_sales_inquiries.html', context)


# --- 9. FARMER ORDER ACTIONS (Accept/Reject) ---
@login_required
def accept_order(request, order_item_pk):
    if request.method != 'POST':
        return redirect('livestock:sales_inquiries')

    if not hasattr(request.user, 'farmer_profile'):
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    order_item = get_object_or_404(OrderItem, pk=order_item_pk)
    
    if order_item.livestock.farmer != request.user.farmer_profile:
        messages.error(request, "Error: You do not own this livestock item.")
        return redirect('livestock:sales_inquiries')

    if order_item.order.order_status != 'pending_inquiry':
        messages.warning(request, "This order has already been processed.")
        return redirect('livestock:sales_inquiries')

    order_item.order.order_status = 'confirmed'
    order_item.order.payment_status = 'confirmed' 
    order_item.order.save()

    livestock = order_item.livestock
    livestock.status = 'sold'
    livestock.is_for_sale = False
    livestock.save()

    messages.success(request, f"Sale approved! Livestock ID {livestock.tag_id} marked as confirmed sale.")
    return redirect('livestock:sales_inquiries')


@login_required
def reject_order(request, order_item_pk):
    if request.method != 'POST':
        return redirect('livestock:sales_inquiries')
    
    if not hasattr(request.user, 'farmer_profile'):
        messages.error(request, "Access denied.")
        return redirect('dashboard')
        
    order_item = get_object_or_404(OrderItem, pk=order_item_pk)

    if order_item.order.order_status != 'pending_inquiry':
        messages.warning(request, "This order has already been processed.")
        return redirect('livestock:sales_inquiries')
        
    order_item.order.order_status = 'rejected'
    order_item.order.save()

    messages.info(request, f"Inquiry #{order_item.order.order_id} has been rejected.")
    return redirect('livestock:sales_inquiries')