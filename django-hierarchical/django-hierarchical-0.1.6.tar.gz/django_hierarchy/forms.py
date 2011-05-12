#!/usr/bin/env python
# encoding: utf-8

from django.forms import ChoiceField, Select, ValidationError

class HierarchicalSelect(Select):
	jquery_namespace = 'django.jQuery'
	
	def __init__(self, *args, **kwargs):
		self.jquery_namespace = kwargs.pop('jquery_namespace', self.jquery_namespace)
		super(HierarchicalSelect, self).__init__(*args, **kwargs)
	
	def render(self, name, value, attrs = None, choices = ()):
		from django.utils.safestring import mark_safe
		from django.forms.util import flatatt
		
		if value is None:
			value = ''
		
		final_attrs = self.build_attrs(attrs, name = name, value = value)
		output = [u'<input type="hidden" %s />' % flatatt(final_attrs)]
		
		def choicedict(choices, parent = None):
			cd = {}
			
			for (i, n, c) in choices:
				d = {
					'n': n,
					'c': choicedict(c, i),
				}
				
				if parent:
					d['p'] = parent
				
				cd[i] = d
			
			return cd
		
		from django.utils import simplejson
		
		choice_dict = choicedict(self.choices)
		js_name = name.replace('-', '__')
		
		def render_select(values):
			output = []
			index = 0
			choices = self.choices
			cd = choice_dict
			parent_value = 0
			
			for value in values:
				output.append(u'<select id="%s_%d">' % (name, index))
				output.append(u'<option value="%d">---</option>' % parent_value)
				options = self.render_options(choices, [value], max_depth = 1)
				
				if options:
					output.append(options)
				
				output.append('</select>');
				
				for (v, n, c) in choices:
					if int(v) == int(value):
						choices = c
				
				output.append('<script type="text/javascript">')
				output.append('%s(document).ready(function() {' % self.jquery_namespace)
				output.append(
					'prepare_%(name)s_options(%(index)d, %(dump)s);' % {
						'name': js_name,
						'index':  index,
						'dump': simplejson.dumps(cd)
					}
				)
				
				output.append('});</script>')
				index += 1
				parent_value = value
				cd = cd.get(value, {'c': {}}).get('c')
			
			return ''.join(output)
		
		if value and value != '':
			def parentage(value, choices):
				ps = []
				
				for k, v in choices.items():
					if int(k) == int(value):
						p = v.get('p')
						
						if not p is None:
							ps.append(p)
							ps.extend(
								parentage(p, choice_dict)
							)
					else:
						ps.extend(
							parentage(value, v['c'])
						)
				
				return ps
			
			values = parentage(value, choice_dict)
			values.insert(0, int(value))
			values.reverse()
			
			def childcount(value, choices):
				for k, v in choices.items():
					if int(k) == int(value):
						return len(v['c'])
					else:
						cc = childcount(value, v['c'])
						if cc > 0:
							return cc
							
				return 0
			
			if childcount(value, choice_dict) > 0:
				values.append(0)
			
			output.append(
				render_select(values)
			)
		else:
			output.append(
				render_select([0])
			)
			
			values = []
		
		output.append(
			'<script type="text/javascript">var %s_options = %s;' % (
				js_name, simplejson.dumps(choice_dict)
			)
		)
		
		output.append('var %s_field_index = %d;' % (js_name, len(values) - 1))
		output.append('var %s_selects = {' % js_name)
		
		for i, value in enumerate(values):
			output.append(
				'"%(id)d": "%(name)s_%(id)d"' % {
					'id': i,
					'name': name
				}
			)
			
			if i + 1 < len(values):
				output.append(',')
		
		output.append('};</script>')
		output.append('<script type="text/javascript">')
		output.append('\tfunction clear_%s_subselects(index) {' % js_name)
		output.append('\t\tfor(i in %s_selects) {' % js_name)
		output.append('\t\t\tif(i > index) {')
		output.append('\t\t\t\tid = %s_selects[i];' % js_name)
		output.append('\t\t\t\t%s("#" + id).remove();' % self.jquery_namespace)
		output.append('\t\t\t\t%s_selects[i] = null;' % js_name)
		output.append('\t\t\t}')
		output.append('\t\t}')
		output.append('\t\t%s_field_index = index;' % js_name)
		output.append('\t}')
		
		output.append('\tfunction prepare_%s_options(index, choices) {' % js_name)
		output.append(
			'\t\t%s("#%s_" + index).bind("change", function(e) {' % (
				self.jquery_namespace, name
			)
		)
		
		output.append(
			'\t\t%(jq)s("#id_%(name)s").val(%(jq)s(this).val())' % {
				'name': name,
				'jq': self.jquery_namespace
			}
		)
		
		output.append('\t\tclear_%s_subselects(index);' % js_name)
		output.append('\t\tvar id = %s(this).val();' % self.jquery_namespace)
		output.append('\t\tif(choices[id] !== undefined) {')
		output.append('\t\t\tsubchoices = choices[id]["c"];')
		
		output.append('\t\t\tarray_count = 0;')
		output.append('\t\t\tfor(i in subchoices) { array_count ++; }')
		output.append('\t\t\t\tif(array_count == 0) { return; }')
		
		output.append('\t\t\t\t\tvar select_id = "%s_" + (index + 1);' % name)
		output.append(
			'\t\t\t\t\tif(%(name)s_selects[index + 1]) {' % {
				'name': js_name
			}
		)
		
		output.append('\t\t\t\t\t} else { ')
		output.append(
			'\t\t\t\t\t\t%s(this).after("<select id=" + select_id + "></select>");' % \
				self.jquery_namespace
		)
		
		output.append(
			'\t\t\t\t\t\t%(name)s_selects[index + 1] = select_id' % {
				'name': js_name
			}
		)
		
		output.append('\t\t\t\t\t}')
		
		output.append('\t\t\t\t\toptions_html = "<option value=" + id + ">---</option>";')
		output.append('\t\t\t\t\tfor(i in subchoices) {')
		output.append('\t\t\t\t\t\tchoice = subchoices[i];')
		output.append('\t\t\t\t\t\toptions_html += "<option value=" + i + \
			">" + choice["n"] + "</option>";')
		output.append('\t\t\t\t\t}')
		output.append('\t\t\t\t\t%s("#" + select_id).html(options_html)' % \
			self.jquery_namespace)
		output.append(
			'\t\t\t\t\tprepare_%s_options(index + 1, subchoices);' % js_name
		)
		output.append('\t\t\t\t} else {')
		output.append('\t\t\t\t\tclear_%s_subselects(index);' % js_name)
		output.append('\t\t\t\t}')
		output.append('\t\t\t}')
		output.append('\t\t);')
		
		output.append('\t\t%s_field_index = index;' % js_name)
		output.append('\t}')
		output.append('</script>')
		
		return mark_safe(u'\n'.join(output))
	
	def render_options(self, choices, selected_choices, max_depth = -1):
		from django.utils.encoding import StrAndUnicode, force_unicode
		from django.utils.html import escape, conditional_escape
		from itertools import chain
		
		def render_option(option_value, option_label, children, depth = 0):
			option_value = force_unicode(option_value)
			selected_html = (option_value in selected_choices) and \
				u' selected="selected"' or ''
			items = []
			
			items.append(
				u'<option value="%s"%s>%s%s</option>' % (
				escape(option_value), selected_html,
				'&nbsp;' * depth * 3,
				conditional_escape(force_unicode(option_label)))
			)
			
			if depth + 1 < max_depth or max_depth == -1:
				for (child_option, child_label, child_children) in children:
					items.append(
						render_option(child_option, child_label, child_children, depth + 1)
					)
				
			return ''.join(items)
		
		# Normalize to strings.
		selected_choices = set([force_unicode(v) for v in selected_choices])
		output = []
		
		for option_value, option_label, children in choices:
			output.append(
				render_option(option_value, option_label, children)
			)
		
		return u'\n'.join(output)

class HierarchicalChoiceField(ChoiceField):
	widget = HierarchicalSelect
	
	def __init__(self, queryset, *args, **kwargs):
		super(HierarchicalChoiceField, self).__init__(*args, **kwargs)
		self.queryset = queryset
		self.choices = queryset.get_tree()
	
	def valid_value(self, value):
		return isinstance(value, self.queryset.model)
	
	def to_python(self, value):
		from django.core.validators import EMPTY_VALUES
		
		print value
		if value in EMPTY_VALUES:
			return None
		
		try:
			value = self.queryset.get(pk = value)
		except self.queryset.model.DoesNotExist:
			raise ValidationError(self.error_messages['invalid_choice'] % {'value': value})
		
		return value