# Views handling livestock listing and detail pages

import requests
import uuid
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LivestockItemForm, LivestockImageForm, SimpleOrderForm, CheckoutContactForm
from .models import LivestockItem, LivestockImage, Order, OrderItem
from django.http import JsonResponse
from livestock.models import Wishlist, Order, OrderItem
from decimal import Decimal, InvalidOperation
from livestock.models import LivestockItem, LivestockSpecies   


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
    # base queryset: only available + for sale
    listings = LivestockItem.objects.filter(status="available", is_for_sale=True)

    # species choices for the dropdown (distinct species that actually exist in listings)
    species_qs = LivestockSpecies.objects.filter(
        livestock_items__in=listings   # use the correct related_name
    ).distinct()


    # locations for dropdown
    locations_qs = (
        listings.values_list("farmer__farm_location", flat=True)
        .exclude(farmer__farm_location__isnull=True)
        .exclude(farmer__farm_location__exact="")
        .distinct()
    )
    locations = sorted(locations_qs)

    # --- read filters from GET ---
    species_id = request.GET.get("species")  # will be like "3"
    location = request.GET.get("location") or ""
    min_price_raw = request.GET.get("min_price") or ""
    max_price_raw = request.GET.get("max_price") or ""

    # species filter (by id)
    if species_id:
        listings = listings.filter(species_id=species_id)

    # location filter
    if location:
        listings = listings.filter(farmer__farm_location=location)

    # price filters
    try:
        if min_price_raw:
            min_price = Decimal(min_price_raw)
            listings = listings.filter(price__gte=min_price)
    except (InvalidOperation, TypeError):
        min_price_raw = ""

    try:
        if max_price_raw:
            max_price = Decimal(max_price_raw)
            listings = listings.filter(price__lte=max_price)
    except (InvalidOperation, TypeError):
        max_price_raw = ""

    context = {
        "listings": listings,
        "species_list": species_qs,
        "locations": locations,
        "selected_species": species_id,
        "selected_location": location,
        "selected_min_price": min_price_raw,
        "selected_max_price": max_price_raw,
    }
    return render(request, "marketplace.html", context)


# 5. DETAIL VIEW
def livestock_detail(request, pk):
    item = get_object_or_404(LivestockItem, pk=pk)
    
    # Get related items from the same farmer
    related_items = LivestockItem.objects.filter(
        farmer=item.farmer,
        status='available',
        is_for_sale=True
    ).exclude(pk=pk)[:4]
    
    context = {
        'item': item,
        'related_items': related_items,
    }
    return render(request, 'livestock_detail.html', context)


# 6. PLACE ORDER VIEW
# @login_required
# def place_order(request, pk):
#     if not hasattr(request.user, 'buyer_profile'):
#         messages.error(request, "Only registered buyers can place orders.")
#         return redirect('dashboard')
        
#     livestock_item = get_object_or_404(LivestockItem, pk=pk)
#     buyer = request.user.buyer_profile

#     # Availability Check
#     if not livestock_item.is_for_sale or livestock_item.status != 'available':
#         messages.error(request, "This item has already been sold.")
#         return redirect('livestock:marketplace')

#     # Duplicate Check
#     existing_order = Order.objects.filter(
#         buyer=buyer, 
#         payment_status='pending',
#         order_items__livestock=livestock_item
#     ).first()

#     if existing_order:
#         messages.info(request, "You already have a pending order for this item. Resuming payment...")
#         return redirect('livestock:retry_payment', pk=existing_order.pk)

#     if request.method == 'POST':
#         form = SimpleOrderForm(request.POST)
#         if form.is_valid():
#             quantity = form.cleaned_data['quantity']
#             amount = livestock_item.price * quantity
#             tx_ref = str(uuid.uuid4())
            
#             new_order = Order.objects.create(
#                 buyer=buyer,
#                 total_amount=amount,
#                 order_status='pending_payment',
#                 payment_status='pending',
#             )
            
#             OrderItem.objects.create(
#                 order=new_order,
#                 livestock=livestock_item,
#                 quantity=quantity,
#                 unit_price_at_time=livestock_item.price,
#             )

#             context = {
#                 'order': new_order,
#                 'item': livestock_item,
#                 'tx_ref': tx_ref
#             }
#             return render(request, 'payment_simulation.html', context)
            
#     return redirect('livestock:livestock_detail', pk=pk)

# 7. PAYMENT CALLBACK
@login_required
def payment_callback(request):
    tx_ref = request.GET.get('tx_ref')
    fake_status = request.GET.get('status') 

    if fake_status == 'success':
        # FIX: Check for both 'pending' AND 'pay_on_delivery'
        order = Order.objects.filter(
            buyer=request.user.buyer_profile, 
            payment_status__in=['pending', 'pay_on_delivery']
        ).last()
        
        if order:
            order.payment_status = 'paid'
            order.order_status = 'confirmed' # This sets it to "Completed"
            order.save()
            
            # Use direct lookup
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

# 10. APPROVE INQUIRY (Updated for Pay-on-Delivery Flow)
@login_required
def approve_inquiry(request, pk):
    inquiry_item = get_object_or_404(OrderItem, pk=pk)
    
    # Permission check
    if inquiry_item.livestock.farmer != request.user.farmer_profile:
        messages.error(request, "You do not have permission to manage this order.")
        return redirect('livestock:sales_inquiries')

    order = inquiry_item.order
    
    # --- CHANGE 1: Update status to APPROVED (not confirmed/sold yet) ---
    order.order_status = 'approved'
    order.save()

    # --- CHANGE 2: Animal stays RESERVED (not sold yet) ---
    # We remove the lines that set status='sold' and is_for_sale=False
    # because the deal is not finished until delivery.
    
    # Optional: Display the delivery address to the farmer in the success message
    address = order.delivery_address or "No address provided"
    
    messages.success(request, f"Inquiry Approved! Deliver to: {address}. The animal remains reserved until payment.")
    return redirect('livestock:sales_inquiries')# 11. REJECT INQUIRY
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

# 12. RETRY PAYMENT
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
    
    if livestock_item.status == 'sold':
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


@login_required
def add_to_order(request, pk):
    item = get_object_or_404(LivestockItem, pk=pk)

    if request.method == 'POST':
        try:
            buyer = request.user.buyer_profile
        except:
            messages.error(request, "You must be a buyer to add items to an order.")
            return redirect('livestock:livestock_detail', pk=pk)

        order, _ = Order.objects.get_or_create(
            buyer=buyer,
            order_status='pending',
            defaults={'total_amount': Decimal('0')}
        )

        order_item, created = OrderItem.objects.get_or_create(
            order=order,
            livestock=item,
            defaults={
                'quantity': 1,
                'unit_price_at_time': item.price or Decimal('0')
            }
        )
        if not created:
            order_item.quantity += 1
            order_item.save()

        # Recalculate total as sum of line prices (no extra tax)
        total = Decimal('0')
        for oi in order.order_items.all():
            line_price = (oi.unit_price_at_time or Decimal('0')) * oi.quantity
            total += line_price

        order.total_amount = total
        order.save()

        messages.success(request, "Item added to your cart.")
        return redirect('livestock:view_cart')

    return redirect('livestock:livestock_detail', pk=pk)



# ADD TO WISHLIST
@login_required
def add_to_wishlist(request, pk):
    item = get_object_or_404(LivestockItem, pk=pk)
    
    if request.method == 'POST':
        try:
            buyer = request.user.buyer_profile
        except:
            return JsonResponse({'message': 'You must be a buyer to save items.', 'success': False})
        
        wishlist, created = Wishlist.objects.get_or_create(user=buyer)
        
        if item in wishlist.items.all():
            wishlist.items.remove(item)
            message = "Removed from Wishlist"
            in_wishlist = False
        else:
            wishlist.items.add(item)
            message = "Added to Wishlist"
            in_wishlist = True
        
        return JsonResponse({'message': message, 'success': True, 'in_wishlist': in_wishlist})
    
    return redirect('livestock:livestock_detail', pk=pk)


@login_required
def view_cart(request):
    try:
        buyer = request.user.buyer_profile
        order = Order.objects.get(buyer=buyer, order_status='pending')
    except Order.DoesNotExist:
        order = None

    if order:
        # Self‑heal: always recompute total from items
        total = Decimal('0')
        for oi in order.order_items.all():
            line_price = (oi.unit_price_at_time or Decimal('0')) * oi.quantity
            total += line_price

        order.total_amount = total
        order.save()

    return render(request, 'cart.html', {'order': order})


@login_required
def remove_from_cart(request, item_id):
    try:
        buyer = request.user.buyer_profile
        order = Order.objects.get(buyer=buyer, order_status='pending')
    except:
        return redirect('livestock:view_cart')

    try:
        order_item = OrderItem.objects.get(order=order, order_item_id=item_id)
        order_item.delete()
    except OrderItem.DoesNotExist:
        pass

    # Recalculate order total after removal (no tax)
    total = Decimal('0')
    for oi in order.order_items.all():
        line_price = (oi.unit_price_at_time or Decimal('0')) * oi.quantity
        total += line_price
    order.total_amount = total
    order.save()

    return redirect('livestock:view_cart')


@login_required
def checkout_cart(request):
    if not hasattr(request.user, 'buyer_profile'):
        messages.error(request, "Only registered buyers can place orders.")
        return redirect('dashboard')

    buyer = request.user.buyer_profile
    order = Order.objects.filter(buyer=buyer, order_status='pending').first()

    if not order:
        messages.error(request, "Cart is empty.")
        return redirect('livestock:marketplace')

    # If request is POST, user submitted the contact info
    if request.method == 'POST':
        form = CheckoutContactForm(request.POST, instance=order)
        if form.is_valid():
            # 1. Save the contact info
            saved_order = form.save(commit=False)
            
            # 2. Update Status to 'inquiry_sent'
            saved_order.order_status = 'inquiry_sent'
            saved_order.save()

            # 3. Reserve the items
            for item in saved_order.order_items.all():
                if item.livestock and item.livestock.status == 'available':
                    item.livestock.status = 'reserved'
                    item.livestock.save()

            messages.success(request, "Inquiry sent! The farmer has received your delivery details and will respond soon.")
            return redirect('livestock:order_history')
    else:
        # Pre-fill phone if available in user profile
        initial_data = {}
        if hasattr(request.user.userprofile, 'phone_number'):
            initial_data['contact_phone'] = request.user.userprofile.phone_number
        
        form = CheckoutContactForm(instance=order, initial=initial_data)

    return render(request, 'checkout.html', {'form': form, 'order': order})


# THIS VIEW IS FOR LATER: It will be used when the order is 'approved' and delivered.
@login_required
def payment_simulation(request, pk):
    order = get_object_or_404(Order, pk=pk)
    buyer = request.user.buyer_profile

    # Security Check: Only allow payment if order belongs to buyer AND is approved by farmer
    if order.buyer != buyer or order.order_status != 'approved':
        messages.error(request, "This order is not ready for payment yet.")
        return redirect('livestock:order_history')

    tx_ref = str(uuid.uuid4())

    # Calculate values for display
    total = order.total_amount or Decimal('0')
    # Recalculate tax for display purposes based on your previous code logic
    VAT_RATE = Decimal('18')
    VAT_DIVISOR = Decimal('118')
    tax = (total * VAT_RATE) / VAT_DIVISOR
    subtotal_net = total - tax

    context = {
        'order': order,
        'tx_ref': tx_ref,
        # Pass calculated values to template
        'subtotal_net': subtotal_net,
        'tax': tax,
    }
    return render(request, 'payment_simulation.html', context)


# 13. EDIT LIVESTOCK
@login_required
def livestock_edit(request, pk):
    # Ensure the item belongs to the logged-in farmer
    item = get_object_or_404(LivestockItem, pk=pk, farmer=request.user.farmer_profile)
    
    if request.method == 'POST':
        form = LivestockItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Livestock details updated successfully.")
            return redirect('dashboard')
    else:
        # Pre-fill the form with existing data
        form = LivestockItemForm(instance=item)
    
    return render(request, 'edit_livestock.html', {'form': form, 'item': item})

# 14. DELETE LIVESTOCK
@login_required
def livestock_delete(request, pk):
    # Ensure the item belongs to the logged-in farmer
    item = get_object_or_404(LivestockItem, pk=pk, farmer=request.user.farmer_profile)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, "Livestock listing deleted.")
        return redirect('dashboard')
        
    # If accessed via GET, redirect back to dashboard (safety)
    return redirect('dashboard')