#!/usr/bin/env python
# encoding: utf-8

from django.contrib import admin
from django import forms
from django_hierarchy.forms import HierarchicalChoiceField

class HierarchicalAdminForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(HierarchicalAdminForm, self).__init__(*args, **kwargs)
		self.fields['parent'] = HierarchicalChoiceField(
			queryset = self.fields['parent'].queryset,
			required = False
		)
		
	def clean_parent(self):
		parent = self.cleaned_data['parent']
		if not self.instance is None and not parent is None:
			if self.instance.pk == parent.pk:
				raise forms.ValidationError(
					'%s cannot be a child of itself' % self.instance._meta.verbose_name.capitalize()
				)
				
		return parent

class HierarchicalAdmin(admin.ModelAdmin):
	list_display = (
		'hierarchical_name',
		'slug',
		'parent'
	)
	
	search_fields = ('name',)
	
	prepopulated_fields = {
		'slug': ('name',)
	}
	
	form = HierarchicalAdminForm
	
	def hierarchical_name(self, obj):
		parents = '&nbsp;&nbsp;&nbsp;&nbsp;' * obj.slug_hierarchical.count('/')
		return '%s%s' % (parents, obj.name)
	hierarchical_name.allow_tags = True
	hierarchical_name.short_description = 'Name'

class SortableHierarchicalAdmin(HierarchicalAdmin):
	list_display = HierarchicalAdmin.list_display + ('order',)
	search_fields = ('name',)