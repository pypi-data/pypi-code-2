from django.contrib import admin
from django import forms
from netcash.models import NetcashGateway, NetcashOrder


class NetcashGatewayAdmin(admin.ModelAdmin):

    class form(forms.ModelForm):
        regenerate_secret = forms.BooleanField(initial=False, required=False,
            help_text='<span style="color:red">Check this in order to regenerate the Data URL. Be careful!</span>')

        def save(self, *args, **kwargs):
            instance = super(NetcashGatewayAdmin.form, self).save(*args, **kwargs)
            if self.cleaned_data['regenerate_secret']:
                instance.secret=None
                instance.save()
            return instance

        class Meta:
            model = NetcashGateway

    list_display = ['name', 'data_url', 'accept_url', 'reject_url', 'netcash_ip']
    readonly_fields = ['data_url', 'accept_url', 'reject_url']

class NetcashOrderAdmin(admin.ModelAdmin):

    def short_debug_info(self, obj):
        if obj.debug_info:
            if len(obj.debug_info) > 15:
                return obj.debug_info[:14]+' ...'
        return obj.debug_info
    short_debug_info.short_description = 'debug info'

    def accepted(self, obj):
        return obj.TransactionAccepted
    accepted.boolean = True
    accepted.admin_order_field = 'TransactionAccepted'

    list_display = ['Reference', 'created_at', 'updated_at', 'Amount',
                    'Reason', 'RETC', 'request_ip', 'accepted',
                    'trusted', 'Extra1', 'Extra2', 'Extra3', 'short_debug_info']
    list_filter = ['TransactionAccepted', 'trusted']
    search_fields = ['Reference']
    date_hierarchy = 'created_at'

admin.site.register(NetcashGateway, NetcashGatewayAdmin)
admin.site.register(NetcashOrder, NetcashOrderAdmin)
