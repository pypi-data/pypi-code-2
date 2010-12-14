#!/usr/bin/env python
#coding=utf8
#
#       Copyright 2010 Antoine Millet <antoine@inaps.org>
#
#       This file is part of DocBucket.
#       
#       Foobar is free software: you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation, either version 3 of the License, or
#       (at your option) any later version.
#       
#       Foobar is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

from django import forms
from helpers import list_document_classes, list_incomings
from itertools import chain

from django.utils.html import escape, conditional_escape
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.datastructures import MultiValueDict, MergeDict
from django.core.urlresolvers import reverse

class PageSelector(forms.Widget):
	def __init__(self, attrs=None, choices=()):
		super(PageSelector, self).__init__(attrs)
		# choices can be any iterable, but we may need to render this widget
		# multiple times. Thus, collapse it into a list so it can be consumed
		# more than once.
		self.choices = list(choices)

	def render(self, name, value, attrs=None, choices=()):
		if value is None: value = []
		final_attrs = self.build_attrs(attrs)
		output = []
		output.append(u'<div id="pages"%s>' % forms.widgets.flatatt(final_attrs))
		output.append(u'<a class="action select" href="#">Select all</a>')
		output.append(u'<a class="action deselect" href="#">Deselect all</a>')
		output.append(u'<ul>')
		pages = self.render_pages(name, choices, value)
		if pages:
			output.append(pages)
		output.append('</ul></div>')
		return mark_safe(u'\n'.join(output))

	def render_pages(self, name, choices, selected_pages):
		selected_pages = tuple([force_unicode(v) for v in selected_pages])
		output = []
		choices = self._reorder_choices_from_selected(selected_pages, chain(self.choices, choices))
		for i, (page_filename, page_name) in enumerate(choices):
			output.append(self.render_page(i, name, selected_pages, page_filename, page_name))
		return u'\n'.join(output)

	def render_page(self, idx, name, selected_pages, page_filename, page_name):
		page_filename = force_unicode(page_filename)
		checked = (page_filename in selected_pages) and u' checked="checked"' or ''
		opts = (reverse('thumb', args=(page_filename,)), name, idx, name, checked,
		        escape(page_filename), name, idx, conditional_escape(force_unicode(page_name)))
		
		return (u'<li><img src="%s" /><p><input id="id_%s_%s" name="%s"%s value="%s" '
		         'type="checkbox" /><label for="id_%s_%s">%s</label></p></li>') % opts

	def value_from_datadict(self, data, files, name):
		if isinstance(data, (MultiValueDict, MergeDict)):
			return data.getlist(name)
		return data.get(name, None)

	def _has_changed(self, initial, data):
		if initial is None:
			initial = []
		if data is None:
			data = []
		if len(initial) != len(data):
			return True
		for value1, value2 in zip(initial, data):
			if force_unicode(value1) != force_unicode(value2):
				return True
		return False

	def _reorder_choices_from_selected(self, selected, choices):
		choices = dict(choices)
		ordered_choices = list(selected)
		for c in choices:
			if c not in ordered_choices:
				ordered_choices.append(c)
		real_choices = []
		for c in ordered_choices:
			real_choices.append((c, choices[c]))
		return real_choices


class CreateDocumentForm(forms.Form):
	name = forms.CharField(max_length=200)
	document_class = forms.ChoiceField(choices=())
#	physical_location = forms.CharField(max_length=50, required=False)
	pages = forms.MultipleChoiceField(choices=(), widget=PageSelector)

	def __init__(self, *args, **kwargs) :
		super(CreateDocumentForm, self) .__init__(*args, **kwargs)
		self.fields['pages'].choices = list_incomings()
		self.fields['document_class'].choices = list_document_classes()


class CreateDocumentClassForm(forms.Form):
	name = forms.CharField(max_length=200)
	slug = forms.CharField(max_length=20)
	
