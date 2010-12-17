from django.conf import settings
from django.db import models
from urlreduce import utils

class Link( models.Model ):
    """
    Link Holds a base URI and a shortened URI, this can be used for both local
    and remote sites.
    """
    
    url         = models.URLField( verify_exists = False, unique = True )
    short_url   = models.URLField( verify_exists = False, blank = True, unique = True )

    def key( self ):
        return utils.base62_encode( self.pk )

    def save( self, *args, **kwargs ):
        """
        Save Override Handles Generating the Short URL
        """
        
        # -- Save to Generate PK
        super( Link, self ).save(*args, **kwargs)
        
        # -- Generate Short URL
        if self.short_url == "" or self.short_url == None:
            self.short_url = settings.URLREDUCE_URL + utils.base62_encode( self.pk )
            super( Link, self ).save(*args, **kwargs)

    def __unicode__( self ):
        return self.short_url