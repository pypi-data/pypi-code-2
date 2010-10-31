#coding: utf-8
from django.contrib import admin
from merchant_api.models import Order, CustomField, Item
from merchant_api.models import OrderChange

class CustomFieldInline(admin.TabularInline):
    model = CustomField
    extra = 0

class ItemInline(admin.StackedInline):
    model = Item
    extra = 0

class OrderChangeInline(admin.TabularInline):
    model = OrderChange
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'created_at', 'amount', 'user_id']
    readonly_fields = ['django_user']
    list_filter = ['is_test']
    inlines = [ItemInline, CustomFieldInline, OrderChangeInline]


class OrderChangeAdmin(admin.ModelAdmin):
    raw_id_fields = ['order']

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderChange, OrderChangeAdmin)
