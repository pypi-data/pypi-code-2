from django.db import models
from django.conf import settings
from photofile.models import *

class Photo(PhotoMetadata):
    image = models.ImageField(upload_to=settings.STATIC_DATA)
    title = models.CharField(max_length=100)

    def __unicode__(self):
        if self.width and self.height:
            return "%s (%sx%s)" % (self.title, self.width, self.height)
        else:
            return self.title
