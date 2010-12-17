from django.contrib import admin

from urlreduce.models import Link

class LinkAdmin( admin.ModelAdmin ):
    """
    Class Defining the Admin Interface for Shortened URL's
    """

    fieldsets = (
        ( "Site", { 'fields': ( 'url', 'short_url' ) } ),
    )
    
    list_display    = [ 'url', 'short_url', 'key' ]
    
    class Meta:
        ordering = [ 'url' ]

admin.site.register( Link, LinkAdmin )