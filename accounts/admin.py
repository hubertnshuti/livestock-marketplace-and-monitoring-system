from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Farmer, Buyer, ContactMessage


# Inline profile for User admin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "profile"
    fk_name = "user"


# Extend the default User admin to show profile inline
class CustomUserAdmin(DjangoUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ("username", "email", "get_user_type", "is_staff", "is_active")
    # 'profile' does not exist; remove it or use 'userprofile'
    list_select_related = ("userprofile",)

    def get_user_type(self, obj):
        # access the real relation name: userprofile
        if hasattr(obj, "userprofile") and obj.userprofile is not None:
            return obj.userprofile.user_type
        return None

    get_user_type.short_description = "User Type"


# Unregister the default User admin and register the customized one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# Register weak entities
@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ("user", "farm_name", "farm_location", "contact_person")
    search_fields = ("user__username", "farm_name")


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    list_display = ("user", "buyer_type")
    search_fields = ("user__username", "buyer_type")



@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at", "is_handled")
    list_filter = ("is_handled", "created_at")
    search_fields = ("name", "email", "subject", "message")
