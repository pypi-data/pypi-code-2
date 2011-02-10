# Copyright (c) 2010 by Yaco Sistemas <pmartin@yaco.es>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this programe.  If not, see <http://www.gnu.org/licenses/>.

from django import forms
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.forms.fields import IntegerField
from django.forms.models import ModelChoiceField

from genericforeignkey.widgets import (GenericForeignKeyWidget,
                                       RelatedGenericPublicWidget,
                                       RelatedGenericAdminWidget,
                                       RelatedFieldWidgetWrapperWithOutAddLink)


class BaseGenericForeignKeyField(object):

    widget = GenericForeignKeyWidget

    def __init__(self, fields=None, initial=None, filter_content_types=None, exclude_content_types=None, *args, **kwargs):
        if not fields:
            field_contenttype = ModelChoiceField(queryset=ContentType.objects.all())
            field_integer = IntegerField()
            fields = [field_contenttype, field_integer]
        field_contenttype = fields[0]
        field_contenttype.widget.attrs['class'] = 'genericforeignkey'
        if isinstance(field_contenttype.widget, RelatedFieldWidgetWrapper):
            field_contenttype.widget.widget.attrs['class'] = 'genericforeignkey'
        self.exclude_content_types = exclude_content_types or []
        self.filter_content_types = filter_content_types or []
        filters = Q()
        for app_label, model in self.filter_content_types:
            filters = filters | Q(app_label=app_label, model=model)
        field_contenttype.queryset = field_contenttype.queryset.filter(filters)

        for app_label, model in self.exclude_content_types:
            field_contenttype.queryset = field_contenttype.queryset.exclude(app_label=app_label,
                                                                            model=model)
        content_type_widget = self._get_content_type_widget(field_contenttype)
        self.widget = self.widget(widgets=[content_type_widget, self.related_generic_widget], initial=initial)
        super(BaseGenericForeignKeyField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if len(data_list) == 2 and data_list[0] and data_list[1]:
            return data_list[0].model_class().objects.get(id=data_list[1])
        return None


class GenericForeignKeyAdminField(BaseGenericForeignKeyField, forms.MultiValueField):
    related_generic_widget = RelatedGenericAdminWidget

    def _get_content_type_widget(self, field_contenttype):
        content_type_widget = RelatedFieldWidgetWrapperWithOutAddLink(widget=field_contenttype.widget.widget,
                                                                      rel=field_contenttype.widget.rel,
                                                                      admin_site=field_contenttype.widget.admin_site)
        content_type_widget.choices = field_contenttype.widget.choices
        return content_type_widget


class GenericForeignKeyPublicField(BaseGenericForeignKeyField, forms.MultiValueField):
    related_generic_widget = RelatedGenericPublicWidget

    def _get_content_type_widget(self, field_contenttype):
        return field_contenttype.widget
