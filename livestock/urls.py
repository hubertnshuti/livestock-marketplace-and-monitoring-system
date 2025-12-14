from django.urls import path
from . import views


app_name = 'livestock'


urlpatterns = [
    # --- Farmer Flow ---
    path('add/', views.livestock_create, name='livestock_add'),
    path('add/<int:pk>/photos/', views.add_photos, name='add_photos'),
    path('add/success/', views.upload_success, name='upload_success'),
    
    # --- Marketplace & Buying ---
    path('marketplace/', views.marketplace, name='marketplace'),
    path('<int:pk>/', views.livestock_detail, name='livestock_detail'),
    path('<int:pk>/add-to-order/', views.add_to_order, name='add_to_order'),
    path('<int:pk>/add-to-wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    # path('order/<int:order_id>/place-order/', views.place_order, name='place_order'),

    path('cart/', views.view_cart, name='view_cart'),
    
    # --- Payment Callback (THE MISSING LINK) ---
    path('callback/', views.payment_callback, name='payment_callback'),
    
    # --- Dashboards Links ---
    path('history/', views.order_history, name='order_history'),       # For Buyers
    path('sales/', views.sales_inquiries, name='sales_inquiries'),     # For Farmers
    path('inquiry/<int:pk>/approve/', views.approve_inquiry, name='approve_inquiry'),
    path('inquiry/<int:pk>/reject/', views.reject_inquiry, name='reject_inquiry'),
    
    # NEW: Retry Payment Path
    path('order/<int:pk>/pay/', views.retry_payment, name='retry_payment'),
    
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    path('cart/checkout/', views.checkout_cart, name='checkout_cart'),
    
    path('edit/<int:pk>/', views.livestock_edit, name='livestock_edit'),
    path('delete/<int:pk>/', views.livestock_delete, name='livestock_delete'),

]