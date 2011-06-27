# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.db.models.signals import *
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import *
      
#from mptt.models import MPTTModel
#import re
  
#---------------------------------------------------------------
#---------------------------------------------------------------
class SEO(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object=generic.GenericForeignKey('content_type','object_id')
    #
    title_en   =models.CharField(blank=True, max_length=128, help_text='заголовок английской страницы')
    title_ru   =models.CharField(blank=True, max_length=128, help_text='заголовок русской страницы')
    keywords_en=models.TextField(blank=True, help_text='введите английские ключевые слова для страницы через запятую.')
    keywords_ru=models.TextField(blank=True, help_text='введите русские ключевые слова для страницы через запятую.')
    description_en=models.TextField(blank=True, help_text='опишите в 2-3 фразы о чем эта страница на английском языке')
    description_ru=models.TextField(blank=True, help_text='опишите в 2-3 фразы о чем эта страница на русском языке')
    de     = models.DateTimeField(auto_now_add=True)
    lm     = models.DateTimeField(auto_now=True)
    #----------
    def __unicode__(self):
        rv = self.title_ru if self.title_ru else self.title_en
        return rv
    class Meta:
        ordering = ('content_type', 'de')
        #unique_together = ('tree_id','level','slug')
        verbose_name='SEO'
        verbose_name_plural='SEO'
#---------------------------------------------------------------
#---------------------------------------------------------------
