#encoding:utf-8
from django.db import models
from django.contrib.contenttypes import generic
from helmholtz.annotation.models import IntegerAnnotation, StaticDescription
from helmholtz.species.models import Species

class Atlas(models.Model):
    name = models.CharField(max_length=16, primary_key=True)
    
    class Meta:
        verbose_name_plural = 'atlases'

vs_choices = (('V', 'volume'), ('S', 'surface'))
ps_choices = (('P', 'primary'), ('S', 'super'))
class BrainRegion(models.Model):
    id = models.IntegerField(primary_key=True)
    atlas = models.ForeignKey(Atlas, null=True)
    species = models.ForeignKey(Species,null=True)
    abbreviation = models.CharField(max_length=6)
    english_name = models.CharField(max_length=100)
    latin_name = models.CharField(max_length=100)
    volume_or_surface = models.CharField(max_length=1, choices=vs_choices, verbose_name='V or S', help_text='Volume or Surface')
    primary_or_super = models.CharField(max_length=1, choices=ps_choices, verbose_name='P or S', help_text='Primary or Super')
    parent = models.ForeignKey('self', null=True, blank=True)
    
    def __unicode__(self):
        return self.english_name
    shortname = property(__unicode__)

class CellType(models.Model):
    english_name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=6)
    brain_region = models.ForeignKey(BrainRegion, null=True)
    
    def __unicode__(self):
        return self.english_name
    shortname = property(__unicode__)

class Cell(models.Model):
    label = models.CharField(max_length=8, null=True, blank=True)
    type = models.ForeignKey(CellType, null=True)
    properties = models.ManyToManyField(StaticDescription, null=True, blank=True)
    annotation = generic.GenericRelation(IntegerAnnotation, content_type_field='content_type', object_id_field='object_id')
    
    def mapping(self, field_name):
        mapping = {'block':'B'}
        return mapping(field_name)
