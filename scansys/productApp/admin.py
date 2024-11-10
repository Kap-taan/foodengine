# admin.py

from django.contrib import admin
from unfold.admin import ModelAdmin  # Import ModelAdmin from Unfold
from .models import Category, Product, Order, Seat

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    pass

@admin.register(Product)
class ProductAdmin(ModelAdmin):
    pass

@admin.register(Order)
class OrderAdmin(ModelAdmin):

    list_filter = ['order_status', 'seat_number', 'payment_status', 'user']

    class Media:
        js = ("admin/js/my_code.js",)
    pass

@admin.register(Seat)
class SeatAdmin(ModelAdmin):
    pass
