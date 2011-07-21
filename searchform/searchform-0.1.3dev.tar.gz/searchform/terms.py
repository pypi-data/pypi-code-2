# Copyright (c) 2008 by Yaco Sistemas S.L.
# Contact info: Lorenzo Gil Sanchez <lgs@yaco.es>
#
# This file is part of searchform
#
# searchform is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# searchform is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with searchform.  If not, see <http://www.gnu.org/licenses/>.

import copy

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


class BaseSearchTerm(object):
    template = 'base_search_term.html'
    operators = tuple()
    searchlet_type = None

    def __init__(self, label, menuitem_label, query_arg_prefix, template=None):
        self.label = label
        self.menuitem_label = menuitem_label
        self.query_arg_prefix = query_arg_prefix
        self.operators_map = dict(self.operators)
        self.field_name = None
        self.template = template or self.__class__.template

    def is_binded(self):
        return not (self.field_name is None)

    def bind(self, field_name):
        clone = copy.copy(self)
        clone.field_name = field_name
        return clone

    def get_query_arg_as_text(self, operator, value):
        return u'%s %s' % (self.get_description(operator), value)

    def get_description(self, operator):
        operator_label = self.operators_map[operator]
        return u'%s %s' % (self.query_arg_prefix, operator_label)

    def render_searchlet_block(self):
        options = [{'operator': op, 'label': label}
                   for op, label in self.operators]
        context = {
            'field': self,
            'options': options,
            }
        return render_to_string(self.template, context)

    def __unicode__(self):
        return mark_safe(self.render_searchlet_block())


class FreeTextSearchTerm(BaseSearchTerm):
    template = 'free_text_search_term.html'
    operators = (
        ('icontains', _('contains')),
        )
    searchlet_type = 'freetext'

SphinxSearchTerm = FreeTextSearchTerm # backwards compatibility


class TextSearchTerm(BaseSearchTerm):
    operators = (
        ('icontains', _('contains')),
        ('not_icontains', _('does not contains')),
        ('istartswith', _('starts with')),
        ('exact', _('is exactly')),
        )
    searchlet_type = 'text'


class LongTextSearchTerm(TextSearchTerm):
    template = 'long_text_search_term.html'


class DateSearchTerm(BaseSearchTerm):
    operators = (
        ('exact', _('is exactly')),
        ('gt', _('greater than')),
        ('lt', _('less than')),
        ('period', _('period')),
        ('century', _('century')),
        )
    searchlet_type = 'text'


class HiddenSearchTerm(TextSearchTerm):
    operators = (
        ('exact', _('is exactly')),
        ('gt', _('greater than')),
        ('lt', _('less than')),
        ('in', _('is')),
        ('icontains', _('contains')),
        )
    template = 'hidden_search_term.html'
    searchlet_type = 'hidden'
    value = ''

    def get_query_arg_as_text(self, operator, value):
        return u''


class ExclusiveOptionsSearchTerm(BaseSearchTerm):
    options = ()
    template = 'exclusive_options_search_term.html'
    operators = ()
    operator = ''
    operator_label = ''
    searchlet_type = 'exclusive_options'


class MultipleOptionsSearchTerm(BaseSearchTerm):

    select_size = 7
    options = ()
    operators = (
        ('in', _(u'is')),
        )
    operator = operators[0][0]
    operator_label = operators[0][1]
    template = 'multiple_options_search_term.html'
    searchlet_type = 'multiple_options'

    def render_searchlet_block(self):
        options = [{'operator': op, 'label': label}
                   for op, label in self.options]
        context = {
            'field': self,
            'options': options,
            }
        return render_to_string(self.template, context)


class ObjectsSearchTerm(MultipleOptionsSearchTerm):

    model = None
    has_empty_option = False

    def queryset(self):
        return self.model.objects.all()

    def _options(self):
        empty = []
        if self.has_empty_option:
            empty.append(('', '----------'))
        queryset = self.queryset()
        return empty + [(obj.id, unicode(obj)) for obj in queryset]

    options = property(_options)

    def _get_value_text(self, value):
        value_text = []
        if not isinstance(value, list):
            value = [value]
        for obj_id in value:
            obj = self.model.objects.get(id=int(obj_id))
            value_text.append(unicode(obj))
        return u', '.join(value_text)

    def get_query_arg_as_text(self, operator, value):
        if value == '':
            return ''
        value_text = self._get_value_text(value)
        return u'%s %s' % (self.get_description(operator), value_text)


class ExclusiveObjectsSearchTerm(ObjectsSearchTerm):
    template = 'exclusive_select_search_term.html'
    operators = (
        ('exact', _(u'is')),
    )
