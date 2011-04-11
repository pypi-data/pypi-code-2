#!/usr/bin/env python
# encoding: utf-8

from django.db import models
from django_hierarchy.managers import HierarchicalManager

class Hierarchical(models.Model):
	name = models.CharField(max_length = 50)
	slug = models.SlugField(max_length = 20)
	slug_hierarchical = models.CharField(max_length = 255, editable = False, unique = True)
	parent = models.ForeignKey('self', related_name = 'children', null = True)
	objects = HierarchicalManager()
	
	@property
	def ancestor_count(self):
		return self.slug_hierarchical.count('/')
	
	def __unicode__(self):
		return self.name
	
	def save(self, *args, **kwargs):
		from pprint import pprint
		
		pprint('Saving %s' % self)
		
		if self.parent:
			self.slug_hierarchical = '%s/%s' % (self.parent.slug_hierarchical, self.slug)
		else:
			self.slug_hierarchical = self.slug
		
		if not self.pk is None and self.children.count() > 0:
			old = type(self).objects.get(pk = self.pk)
			super(Hierarchical, self).save(*args, **kwargs)
			
			if old.slug_hierarchical != self.slug_hierarchical:
				pprint('Tag changed from %s to %s' % (old.slug_hierarchical, self.slug_hierarchical))
				for child in self.children.all():
					child.save()
			
			return
		
		super(Hierarchical, self).save(*args, **kwargs)
	
	class QuerySet(models.query.QuerySet):
		def get_tree(self):
			from django_hierarchy import helpers
			return helpers.recurse(self.filter(parent__isnull = True))
	
	class Meta:
		abstract = True
		ordering = ('slug_hierarchical',)
		unique_together = ('parent', 'slug')