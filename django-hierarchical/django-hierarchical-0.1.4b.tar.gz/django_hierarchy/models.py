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
	
	def hierarchy_changed(self, old):
		return old.slug_hierarchical != self.slug_hierarchical
	
	def save(self, *args, **kwargs):
		if self.parent:
			self.slug_hierarchical = '%s/%s' % (self.parent.slug_hierarchical, self.slug)
		else:
			self.slug_hierarchical = self.slug
		
		if not self.pk is None and self.children.count() > 0:
			old = type(self).objects.get(pk = self.pk)
			super(Hierarchical, self).save(*args, **kwargs)
			
			if self.hierarchy_changed(old):
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
		
class SortableHierarchical(Hierarchical):
	order = models.PositiveSmallIntegerField(default = 0)
	order_hierarchical = models.CharField(max_length = 255, editable = False)
	
	def hierarchy_changed(self, old):
		changed = super(SortableHierarchical, self).hierarchy_changed(old)
		if not changed:
			return old.order_hierarchical != self.order_hierarchical
		
		return True
	
	def save(self, *args, **kwargs):
		if self.parent:
			self.order_hierarchical = '%s/%s' % (
				str(self.parent.order_hierarchical).zfill(3),
				str(self.order).zfill(3)
			)
		else:
			self.order_hierarchical = str(self.order).zfill(3)
		
		super(SortableHierarchical, self).save(*args, **kwargs)
	
	class Meta:
		abstract = True
		ordering = ('order_hierarchical',)
		unique_together = ('parent', 'slug')