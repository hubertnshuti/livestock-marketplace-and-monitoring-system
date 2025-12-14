from django.contrib import admin
from .models import (
    LivestockSpecies, Breed, LivestockItem, ProductListing,
    IoTDeviceData, Alert, Order, OrderItem
)

@admin.register(LivestockSpecies)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ('id', 'species_name')
    search_fields = ('species_name',)

@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    list_display = ('id', 'species', 'breed_name')
    list_filter = ('species',)
    search_fields = ('breed_name',)

@admin.register(LivestockItem)
class LivestockItemAdmin(admin.ModelAdmin):
    list_display = ('livestock_id', 'farmer', 'species', 'breed', 'tag_id', 'status', 'is_for_sale', 'price')
    list_filter = ('species', 'status', 'is_for_sale')
    search_fields = ('tag_id', 'description', 'farmer__farm_name')

@admin.register(ProductListing)
class ProductListingAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'product_name', 'farmer', 'price_per_unit', 'units_available')
    search_fields = ('product_name', 'farmer__farm_name')

@admin.register(IoTDeviceData)
class IoTDeviceDataAdmin(admin.ModelAdmin):
    list_display = ('data_id', 'livestock', 'timestamp', 'temperature', 'battery_level')
    search_fields = ('livestock__tag_id',)

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('alert_id', 'alert_type', 'farmer', 'livestock', 'severity', 'is_resolved', 'timestamp')
    list_filter = ('severity', 'is_resolved')
    search_fields = ('alert_type', 'farmer__farm_name')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'buyer', 'order_date', 'total_amount', 'order_status', 'payment_status')
    list_filter = ('order_status', 'payment_status')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order_item_id', 'order', 'livestock', 'product', 'quantity', 'unit_price_at_time')
    search_fields = ('order__order_id',)
