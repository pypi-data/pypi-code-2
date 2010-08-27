#encoding:utf-8
from django.db import models

class Species(models.Model):
    """Species of a Subject.""" 
    id = models.PositiveIntegerField(primary_key=True, help_text="catalog of life unique identifier")
    scientific_name = models.CharField(max_length=300, unique=True)
    english_name = models.CharField(max_length=300, null=True, blank=True)
    codename = models.CharField(max_length=30, null=True, blank=True)
    lsid = models.TextField(unique=True, null=True, blank=True)
    url = models.URLField(verify_exists=False, null=True, blank=True)
    
    def __unicode__(self):
        return self.english_name
    
    class Meta:
        verbose_name_plural = "species"
        ordering = ['english_name']
 
class Strain(models.Model):
    """Strain of a Subject."""
    name = models.CharField(primary_key=True, max_length=32)
    species = models.ForeignKey(Species)
    genotype = models.CharField(max_length=300, null=True, blank=True)
    notes = models.TextField(null=True, blank=True) 
    
    def __unicode__(self):
        return "%s(%s)" % (self.species, self.name)
