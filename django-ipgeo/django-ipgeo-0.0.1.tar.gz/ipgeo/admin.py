# -*- coding: utf-8
from django.contrib import admin

from ipgeo.models import Location, Range

class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'area']
    search_fields = ['name', 'region', 'area']


class RangeAdmin(admin.ModelAdmin):
    list_display = ['description', 'country', 'location']
    search_fields = ['description', 'location__name']


admin.site.register(Location, LocationAdmin)
admin.site.register(Range, RangeAdmin)
