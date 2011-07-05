#-*- coding: utf-8 -*-
from django.db import models

class Page(models.Model):
    name = models.CharField(max_length=250)
    
    def __unicode__(self):
        return self.name
    
class BaseContent(models.Model):
    page = models.ForeignKey(Page)
    name = models.CharField(max_length=250, editable=False)
    admin_label = models.CharField(max_length=250)
    position = models.IntegerField(default=1, editable=False)
    
    def __unicode__(self):
        return self.admin_label

    class Meta:
        abstract = True
        ordering = ["position"]
    
    
class TextContent(BaseContent):
    text = models.TextField(verbose_name="Current text")
    
    
class ImageContent(BaseContent):
    image = models.ImageField(upload_to="photos")
    width = models.IntegerField(default=150, editable=False)
    height = models.IntegerField(default=150, editable=False)
    
    
        
        
