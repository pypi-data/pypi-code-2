#-*- coding: utf-8 -*-
from django.db import models
from django.contrib import admin
from form_utils.widgets import ImageWidget
from models import TextContent, ImageContent, Page

class TextContentInline(admin.StackedInline):
    fields = ('admin_label', 'text')
    model = TextContent
    extra = 0
    readonly_fields = ('admin_label', )
 
class ImageContentInline(admin.StackedInline):
    fields = ('admin_label', 'width', 'height', 'image')
    model = ImageContent
    extra = 0
    readonly_fields = ('admin_label', 'width', 'height')
    formfield_overrides = { models.ImageField: {'widget': ImageWidget}}
    
class PageAdmin(admin.ModelAdmin):
    inlines = [TextContentInline, ImageContentInline]

admin.site.register(Page, PageAdmin)
