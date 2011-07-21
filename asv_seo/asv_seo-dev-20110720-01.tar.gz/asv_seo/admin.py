from __future__ import unicode_literals
    
from django.contrib import admin
from django.contrib.contenttypes import generic
from django.forms import TextInput, Textarea


from asv_seo.models import *
          
WideTextInput = 64
#---------------------------------------------------------------
#---------------------------------------------------------------
class SEOInline(generic.GenericStackedInline):
    model = SEO
    extra=1
    max_num=1
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs ={'rows': '3'})},
    }
#---------------------------------------------------------------
#---------------------------------------------------------------
class SEOInline_ru(SEOInline):
    fields=['title_ru','keywords_ru','description_ru']
#---------------------------------------------------------------
#---------------------------------------------------------------
class SEOInline_en(SEOInline):
    fields=['title_en','keywords_en','description_en']
#---------------------------------------------------------------
#---------------------------------------------------------------
