#!/usr/bin/env python
# encoding: utf-8

from django.db.models import Manager

class HierarchicalManager(Manager):
	def get_tree(self):
		return self.get_query_set().get_tree()
	
	def get_query_set(self):
		return self.model.QuerySet(self.model)