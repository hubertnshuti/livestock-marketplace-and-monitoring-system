from django.db import models
from django.conf import settings
from django.utils import timezone

# 4. LivestockSpecies (Reference/Lookup Table)
class LivestockSpecies(models.Model):
    species_name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.species_name


# 5. Breed (dependent on Species)
class Breed(models.Model):
    species = models.ForeignKey(LivestockSpecies, on_delete=models.CASCADE, related_name='breeds')
    breed_name = models.CharField(max_length=120)

    class Meta:
        unique_together = ('species', 'breed_name')

    def __str__(self):
        return f"{self.species.species_name} - {self.breed_name}"


# 6. LivestockItem
class LivestockItem(models.Model):
    GENDER_CHOICES = (('male', 'Male'), ('female', 'Female'), ('unknown', 'Unknown'))
    HEALTH_STATUS_CHOICES = (('healthy', 'Healthy'), ('warning', 'Warning'), ('sick', 'Sick'), ('verified', 'Verified'))
    STATUS_CHOICES = (('available', 'Available'), ('sold', 'Sold'), ('reserved', 'Reserved'), ('hidden', 'Hidden'))

    livestock_id = models.AutoField(primary_key=True)  # LivestockID PK
    farmer = models.ForeignKey('accounts.Farmer', on_delete=models.CASCADE, related_name='livestock_items')
    species = models.ForeignKey(LivestockSpecies, on_delete=models.PROTECT, related_name='livestock_items')
    breed = models.ForeignKey(Breed, on_delete=models.SET_NULL, null=True, blank=True, related_name='livestock_items')
    tag_id = models.CharField(max_length=120, unique=True, blank=True, null=True)  # IoT tag
    age = models.PositiveIntegerField(blank=True, null=True)  # in months or years (specify in UI)
    weight = models.FloatField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='unknown')
    health_status = models.CharField(max_length=20, choices=HEALTH_STATUS_CHOICES, default='healthy')
    description = models.TextField(blank=True, null=True)
    listing_date = models.DateTimeField(default=timezone.now)
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    is_for_sale = models.BooleanField(default=False)
    current_location = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        # show a friendly label
        label = self.tag_id or f"ID-{self.livestock_id}"
        return f"{label} ({self.species.species_name})"


# 7. ProductListing (for non-animal products)
class ProductListing(models.Model):
    product_id = models.AutoField(primary_key=True)
    farmer = models.ForeignKey('accounts.Farmer', on_delete=models.CASCADE, related_name='product_listings')
    livestock = models.ForeignKey(LivestockItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='product_listings')
    product_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    units_available = models.PositiveIntegerField(default=0)
    listing_date = models.DateTimeField(default=timezone.now)
    product_category = models.CharField(max_length=120, blank=True, null=True)

    def __str__(self):
        return f"{self.product_name} - {self.farmer.user.username}"


# 8. IoTDeviceData
class IoTDeviceData(models.Model):
    data_id = models.AutoField(primary_key=True)
    livestock = models.ForeignKey(LivestockItem, on_delete=models.CASCADE, related_name='iot_data')
    timestamp = models.DateTimeField(default=timezone.now)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    temperature = models.FloatField(blank=True, null=True)
    activity_level = models.FloatField(blank=True, null=True)
    battery_level = models.FloatField(blank=True, null=True)
    device_type = models.CharField(max_length=120, blank=True, null=True)

    def __str__(self):
        return f"IoT {self.data_id} for {self.livestock}"


# 9. Alert
class Alert(models.Model):
    alert_id = models.AutoField(primary_key=True)
    livestock = models.ForeignKey(LivestockItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='alerts')
    farmer = models.ForeignKey('accounts.Farmer', on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=120)
    timestamp = models.DateTimeField(default=timezone.now)
    SEVERITY_CHOICES = (('critical', 'Critical'), ('warning', 'Warning'), ('info', 'Info'))
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='info')
    is_resolved = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.alert_type} - {self.farmer.user.username}"


# 10. Order
class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    buyer = models.ForeignKey('accounts.Buyer', on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ORDER_STATUS = (
        ('pending', 'Pending (In Cart)'), # Kept for temporary cart state
        ('inquiry_sent', 'Inquiry Sent (Waiting for Farmer)'), # New state after checkout
        ('approved', 'Order Approved (Ready for Payment/Delivery)'), # New state after farmer clicks yes
        ('confirmed', 'Completed (Paid & Delivered)'),
        ('cancelled', 'Cancelled')
    )
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    PAYMENT_STATUS = (('pay_on_delivery', 'Pay on Delivery'), ('paid', 'Paid'))
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pay_on_delivery')
    
    delivery_address = models.TextField(blank=True, null=True, help_text="Where should this be delivered?")
    contact_phone = models.CharField(max_length=15, blank=True, null=True, help_text="Phone number for delivery coordination")

    def __str__(self):
        return f"Order {self.order_id} by {self.buyer.user.username}"


# 11. OrderItem
class OrderItem(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    livestock = models.ForeignKey(LivestockItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    product = models.ForeignKey(ProductListing, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price_at_time = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"OrderItem {self.order_item_id} (Order {self.order.order_id})"


class LivestockImage(models.Model):
    livestock = models.ForeignKey(LivestockItem, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='livestock_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.livestock.tag_id}"
    
# WISHLIST MODEL
class Wishlist(models.Model):
    user = models.OneToOneField('accounts.Buyer', on_delete=models.CASCADE, related_name='wishlist')
    items = models.ManyToManyField(LivestockItem, related_name='wishlists')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wishlist for {self.user.user.username}"
