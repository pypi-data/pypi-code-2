from math import cos, radians
from django.contrib.auth.models import User
from django import forms
from django.db import models
from widgets import *
    
# credits to : http://blog.fedecarg.com/2009/02/08/geo-proximity-search-the-haversine-equation/
from locationbase.widgets import LocationField

def calculate_minmax_radius(lat, long, radius, use_km = True):
    if use_km:
        radius = radius * 0.621371192;

    degradius = radius / 69

    lng_min = long - radius / abs(cos(radians(lat)) * 69)
    lng_max = long + radius / abs(cos(radians(lat)) * 69)
    lat_min = lat - degradius
    lat_max = lat + degradius
    return lng_min, lng_max, lat_min, lat_max


class LocationBase(models.Model):

    class Meta:
        abstract = True
        
    longitude = models.FloatField(null = True, blank = True)
    latitude = models.FloatField(null = True, blank = True)
    altitude = models.FloatField(null = True, blank = True)

    @classmethod
    def items_in_radius(cls, lat, long, radius = 10, use_km = True):
        lng_min, lng_max, lat_min, lat_max = calculate_minmax_radius(lat, long, radius, use_km)
        return cls.objects.filter(longitude__range(lng_min, lng_max), latitude__range(lat_min, lat_max))


class Location(LocationBase):
    """
    """
    location = LocationField(blank=True, max_length=255)
    name = models.CharField(max_length = 100)
    street_address = models.CharField(max_length = 100, null = True, blank = True)
    street_number =  models.CharField(max_length = 10, null = True, blank = True)
    city = models.CharField(max_length = 32, null = True, blank = True)
    zip_code = models.CharField(max_length = 20, null = True, blank = True)
    province_state = models.CharField(max_length = 32, null = True, blank = True)
    country_code = models.CharField(max_length = 3, null = True, blank = True)
    country_name = models.CharField(max_length = 32, null = True, blank = True)
    tagname = models.CharField(max_length = 50, null = True, blank = True)
    owner = models.ForeignKey(User, null = True, blank = True)
    approximation = models.NullBooleanField(null=True, blank=True, default=True)
    public = models.NullBooleanField(null=True, blank=True, default=True)

    def __unicode__(self):
        return self.name


class LocationForm(forms.ModelForm):
    """
    """
    class Meta:
        model = Location
        exclude = ['owner', ]