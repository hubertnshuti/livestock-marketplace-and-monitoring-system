from django.urls import path
from . import views

app_name = 'livestock'

urlpatterns = [
    # --- FARMER ROUTES ---
    path('add/', views.livestock_create, name='livestock_add'),
    path('add/<int:pk>/photos/', views.add_photos, name='add_photos'),
    path('add/success/', views.upload_success, name='upload_success'),
    path('sales/', views.sales_inquiries, name='sales_inquiries'),  # Farmer Sales Page

    # --- BUYER ROUTES ---
    path('marketplace/', views.marketplace, name='marketplace'),
    path('history/', views.order_history, name='order_history'),    # <--- THIS WAS MISSING
    
    # --- SHARED / ITEM ROUTES ---
    path('<int:pk>/', views.livestock_detail, name='livestock_detail'),
    path('<int:pk>/place-order/', views.place_order, name='place_order'),
    path('history/<int:pk>/', views.order_detail, name='order_detail'),
]