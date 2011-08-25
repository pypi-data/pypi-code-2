from django.contrib import admin
from locationbase.models import Location

class LocationAdmin(admin.ModelAdmin):
    fields = ('location', 'name', 'street_address', 'street_number', 'city', 'zip_code', 'country_name', 'country_code', 'province_state', 'altitude', 'longitude', 'latitude', 'public', 'approximation', 'tagname', )
    
    list_display = ('name', 'street_address', 'street_number', 'city', 'zip_code', 'country_code', 'tagname', 'owner', 'public', 'longitude', 'latitude', 'altitude',)
    list_filter = ('owner', 'city', 'zip_code', 'country_code', 'province_state', 'owner', 'public',)

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        super(Location, obj).save()

admin.site.register(Location, LocationAdmin)