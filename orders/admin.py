from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'buyer',
        'status',
        'paid',
        'created'
    ]

    list_filter = [
        'status',
        'paid',
        'created'
    ]

    inlines = [OrderItemInline]