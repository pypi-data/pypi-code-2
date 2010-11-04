from django.contrib import admin
from netcash.models import NetcashGateway, NetcashOrder

class NetcashGatewayAdmin(admin.ModelAdmin):
    list_display = ['name', 'data_url', 'accept_url', 'reject_url', 'netcash_ip']

class NetcashOrderAdmin(admin.ModelAdmin):

    def short_debug_info(self, obj):
        if obj.debug_info:
            if len(obj.debug_info) > 15:
                return obj.debug_info[:15]+' ...'
        return obj.debug_info
    short_debug_info.short_description = 'debug info'

    list_display = ['Reference', 'created_at', 'updated_at', 'Amount',
                    'Reason', 'RETC', 'request_ip', 'TransactionAccepted', 'trusted', 'short_debug_info']
    list_filter = ['TransactionAccepted', 'trusted']
    search_fields = ['Reference']
    date_hierarchy = 'created_at'

admin.site.register(NetcashGateway, NetcashGatewayAdmin)
admin.site.register(NetcashOrder, NetcashOrderAdmin)
