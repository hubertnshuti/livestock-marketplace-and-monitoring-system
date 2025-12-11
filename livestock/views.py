from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LivestockItemForm, LivestockImageForm, SimpleOrderForm
from .models import LivestockItem, LivestockImage, Order, OrderItem, LivestockSpecies

# 1. CREATE BASIC INFO (Step 1)
# Auto-publishes animals to the marketplace immediately
@login_required
def livestock_create(request):
    if request.method == 'POST':
        form = LivestockItemForm(request.POST)
        if form.is_valid():
            livestock_item = form.save(commit=False)
            
            # --- FORCE VISIBILITY SETTINGS ---
            livestock_item.is_for_sale = True       # Automatically put on market
            livestock_item.status = 'available'     # Automatically set status
            # ---------------------------------

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

# 2. ADD PHOTOS VIEW (Step 2)
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

# 3. SUCCESS VIEW (Step 3)
@login_required
def upload_success(request):
    return render(request, 'upload_success.html')

# 4. MARKETPLACE VIEW (Show All + Search)
def marketplace(request):
    # Show ALL animals (removed the .filter(is_for_sale=True) restriction)
    listings = LivestockItem.objects.all().order_by('-listing_date')
    
    # Get filter parameters
    species_query = request.GET.get('species')
    max_price = request.GET.get('max_price')
    
    # Apply Species Filter
    if species_query and species_query != "All Species" and species_query != "":
        listings = listings.filter(species__species_name__iexact=species_query)
        
    # Apply Price Filter
    if max_price and max_price != "":
        try:
            listings = listings.filter(price__lte=int(max_price))
        except ValueError:
            pass 

    all_species = LivestockSpecies.objects.all()

    context = {
        'listings': listings,
        'all_species': all_species,
        'page_title': 'Marketplace',
        'current_species': species_query,
        'current_price': max_price
    }
    return render(request, 'marketplace.html', context)

# 5. DETAIL VIEW (Single Item)
def livestock_detail(request, pk):
    livestock = get_object_or_404(LivestockItem, pk=pk)
    photos = livestock.images.all()
    context = {
        'livestock': livestock,
        'photos': photos,
        'page_title': f"{livestock.species.species_name} Details"
    }
    return render(request, 'livestock_detail.html', context)

# 6. ORDER PLACEMENT VIEW
@login_required
def place_order(request, pk):
    if not hasattr(request.user, 'buyer_profile'):
        messages.error(request, "Only registered buyers can place orders.")
        return redirect('dashboard')
        
    livestock_item = get_object_or_404(LivestockItem, pk=pk)
    buyer = request.user.buyer_profile

    # We typically check availability, but for now we let buyers inquire on anything visible
    # if livestock_item.status != 'available': ...

    if request.method == 'POST':
        form = SimpleOrderForm(request.POST)
        if form.is_valid():
            
            # Create the Order
            new_order = Order.objects.create(
                buyer=buyer,
                total_amount=livestock_item.price * form.cleaned_data['quantity'],
                order_status='pending_inquiry',
                payment_status='pending'
            )
            
            # Create the OrderItem
            OrderItem.objects.create(
                order=new_order,
                livestock=livestock_item,
                quantity=form.cleaned_data['quantity'],
                unit_price_at_time=livestock_item.price,
            )

            messages.success(request, f"Inquiry sent! Order #{new_order.order_id} created.")
            return redirect('livestock:order_history') 
            
    return redirect('livestock:livestock_detail', pk=pk)

# 7. BUYER ORDER HISTORY
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

# 8. FARMER SALES INQUIRIES
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

@login_required
def order_detail(request, pk):
    # Get the order (ensure it belongs to the logged-in buyer)
    order = get_object_or_404(Order, pk=pk, buyer=request.user.buyer_profile)
    
    # Get the items (animals) in this order
    order_items = OrderItem.objects.filter(order=order)
    
    context = {
        'order': order,
        'order_items': order_items,
        'page_title': f"Order #{order.order_id}"
    }
    return render(request, 'order_detail.html', context)