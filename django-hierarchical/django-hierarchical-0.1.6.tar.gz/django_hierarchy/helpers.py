#!/usr/bin/env python
# encoding: utf-8

def recurse(children):
	items = []
	
	for c in children.iterator():
		items.append(
			(c.pk, c.name, recurse(c.children))
		)
	
	return items