from django.urls import path
from .views import login_view, register_view, dashboard, profile # <-- Profile view must be imported
from django.contrib.auth.views import LogoutView


urlpatterns = [
    # AUTH VIEWS
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    # Use the cleaner logout definition
    path("logout/", LogoutView.as_view(next_page='/'), name="logout"), 
    
    # DASHBOARD & PROFILE
    path("dashboard/", dashboard, name="dashboard"),
    path("profile/", profile, name="profile"), # <-- ADDED MISSING PROFILE URL
]  
