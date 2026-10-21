from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ["id","username","email","role","is_staff","is_active"]
    list_filter = ["role","is_staff","is_active",]
    search_fields = ["username","email",]
    fieldsets = UserAdmin.fieldsets + (
        (
            "Marketplace Information",
            {
                "fields": ("role",)
            },
        ),
    )

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["id","user","bio"]
    search_fields = ["user__username","user__email"]