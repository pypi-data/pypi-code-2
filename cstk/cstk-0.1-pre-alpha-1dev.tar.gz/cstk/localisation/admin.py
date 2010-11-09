from django.contrib import admin

from models import Country
from models import Currency
from models import Language
from models import Locale



class CountryAdmin( admin.ModelAdmin ):
    list_display = [ 'name', 'iso_3166_1_alpha2', 'iso_3166_1_alpha3', 'iso_3166_1_numeric', 'iso_3166_2']
    ordering = [ 'name', 'iso_3166_1_alpha2', 'iso_3166_1_alpha3', 'iso_3166_1_numeric', 'iso_3166_2' ]
    search_fields = [ 'name' ]


class CurrencyAdmin( admin.ModelAdmin ):
    list_display = [ 'name', 'iso_4217_alpha', 'iso_4217_numeric' ]
    ordering = [ 'name', 'iso_4217_alpha', 'iso_4217_numeric' ]
    search_fields = [ 'name' ]


class LanguageAdmin( admin.ModelAdmin ):
    list_display = [ 'name', 'native_name', 'iso_639_1', 'iso_639_2t', 'iso_639_2b', 'iso_639_3' ]
    ordering = [ 'name', 'iso_639_1', 'iso_639_2t', 'iso_639_2b', 'iso_639_3' ]
    search_fields = [ 'name', 'native_name' ]


class LocaleAdmin( admin.ModelAdmin ):
    list_display = [ 'name', 'language', 'country' , 'published_status', 'publish_default' ]
    ordering = [ 'name', 'language', 'country' ]
    search_fields = [ 'name', 'language__name', 'country__name' ]
    fields = [ 'language', 'country' ]



admin.site.register( Country, CountryAdmin )
admin.site.register( Currency, CurrencyAdmin )
admin.site.register( Language, LanguageAdmin )
admin.site.register( Locale, LocaleAdmin )
