from django.contrib import admin
from netcash.models import NetcashGateway, NetcashOrder

class NetcashGatewayAdmin(admin.ModelAdmin):
    list_display = ['name', 'data_url', 'accept_url', 'reject_url', 'netcash_ip']

class NetcashOrderAdmin(admin.ModelAdmin):
    list_display = ['Reference', 'created_at', 'Amount', 'RETC', 'TransactionAccepted']
    list_filter = ['gateway']

admin.site.register(NetcashGateway, NetcashGatewayAdmin)
admin.site.register(NetcashOrder, NetcashOrderAdmin)
