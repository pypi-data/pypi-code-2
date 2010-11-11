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

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.datastructures import SortedDict
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _


class SearchForm(object):
    title = ''
    template = 'searchform.html'
    media_template = 'media.html'
    use_tabs = True
    extra_scripts = tuple()

    def __init__(self, title=None, query_string_manager=None,
                 template=None, use_tabs=None, extra_scripts=[]):
        self.title = title or self.__class__.title
        self.qsm = query_string_manager
        self.template = template or self.__class__.template
        if use_tabs is None:
            self.use_tabs = self.__class__.use_tabs
        else:
            self.use_tabs = use_tabs
        self.extra_scripts = extra_scripts or self.__class__.extra_scripts

        # make a private copy of the fields so we don't have unexpected
        # results if somebody else change the class variable
        self.fields = copy.deepcopy(self.__class__.fields)

        self.operators_map = {}
        for field in self.fields.values():
            self.operators_map.update(dict(field.operators))

    def set_qsm(self, query_string_manager):
        self.qsm = query_string_manager

    def get_qsm(self):
        return self.qsm

    def get_search_criteria_as_text(self):
        if self.qsm is None:
            return u''

        result = []

        def add_query_arg(field_name, operator, value):
            if field_name in self.fields:
                field = self.fields[field_name]
                result_field = field.get_query_arg_as_text(operator, value)
                if result_field:
                    result.append(result_field)

        for key, value in self.qsm.get_filters().items():
            field_name, operator = key.rsplit('__', 1)
            add_query_arg(field_name, operator, value)

        for key, value in self.qsm.get_excluders().items():
            field_name, operator = key.rsplit('__', 1)
            add_query_arg(field_name, 'not_' + operator, value)

        separator = u' %s ' % _(u'and')
        return separator.join(result)

    def get_query_args_as_json(self):
        query_args = []

        def add_query_arg(field_name, operator, value):
            if field_name in self.fields:
                field = self.fields[field_name]
                description = field.get_description(operator)
                query_args.append({
                        'attr': field_name,
                        'operator': operator,
                        'value': value,
                        'description': description,
                        'dom': None,
                        })

        if self.qsm:
            for key, value in self.qsm.get_filters().items():
                field_name, operator = key.rsplit('__', 1)
                add_query_arg(field_name, operator, value)

            for key, value in self.qsm.get_excluders().items():
                field_name, operator = key.rsplit('__', 1)
                add_query_arg(field_name, 'not_' + operator, value)

        return simplejson.dumps(query_args, ensure_ascii=False)

    def get_fields_with_query_arg_prefixes(self):
        for field_name, field in self.fields.items():
            yield field_name, field.query_arg_prefix

    def render_media(self):
        context = {
            'MEDIA_URL': settings.MEDIA_URL + 'searchform/',
            'form': self,
            'LANGUAGE_CODE': get_language(),
            }
        return render_to_string(self.media_template, context)

    def binded_fields(self):
        return SortedDict([(field_name, field.bind(field_name))
                           for field_name, field in self.fields.items()])

    def __unicode__(self):
        fields = [field.bind(field_name)
                  for field_name, field in self.fields.items()]
        context = {
            'title': self.title,
            'fields': fields,
            'form': self,
            }
        return mark_safe(render_to_string(self.template, context))


def sanitize_filters(filters):
    """Fix filters by merging related keys

    Example:
    >>> sanitize_filters({'name.operator': 'contains', 'name': 'foo'})
    {'name__contains': 'foo'}
    """
    new_filters = {}
    keys_to_remove = []
    for k, v in filters.items():
        if '.' in k:
            field = k.split('.')[0]
            operator = v
            if isinstance(operator, (list, tuple)):
                operator = operator[0]
            new_key = str('%s__%s' % (field, operator))
            value = filters[field]
            if value:
                new_filters[new_key] = value

            keys_to_remove.append(field)
            if field in new_filters:
                del new_filters[field]

        elif k not in keys_to_remove and v:
            new_filters[k] = v

    return new_filters
