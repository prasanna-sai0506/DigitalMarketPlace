from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id","user","created_at","updated_at"]
    list_filter = ["created_at",]
    search_fields = ["user__username","user__email"]
    inlines = [OrderItemInline,]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["id","order","asset", "quantity","unit_price"]
    search_fields = ["asset__title","order__user__username"]