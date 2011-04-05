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
from django.conf import settings
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from genericforeignkey.fields import (BaseGenericForeignKeyField,
                                      GenericForeignKeyPublicField,
                                      GenericForeignKeyAdminField)


class BaseGenericForm(object):

    FILTER_CONTENT_TYPES = ()
    EXCLUDE_CONTENT_TYPES = ()

    def __init__(self, *args, **kwargs):
        super(BaseGenericForm, self).__init__(*args, **kwargs)
        obj = getattr(self, 'instance', None)
        filter_content_types = getattr(self, 'FILTER_CONTENT_TYPES', []) or \
                               getattr(settings, 'FILTER_CONTENT_TYPES', [])
        exclude_content_types = not filter_content_types and \
                                (getattr(self, 'EXCLUDE_CONTENT_TYPES', []) or \
                                getattr(settings, 'EXCLUDE_CONTENT_TYPES', []))

        if self.data:
            for field_name, field in self.fields.items():
                if isinstance(field, BaseGenericForeignKeyField):
                    generic_foreign_key = field
                    ct_id = self.data.get('%s_0' % field_name, None)
                    fk_id = self.data.get('%s_1' % field_name, None)
                    if ct_id and fk_id:
                        ctype = ContentType.objects.get(pk=ct_id)
                        initial = ctype.model_class().objects.get(pk=fk_id)
                        self.fields[field_name] = self.generic_field(fields=[field.fields[0], field.fields[1]],
                                                                                    initial=field.initial or initial,
                                                                                    filter_content_types=filter_content_types,
                                                                                    exclude_content_types=exclude_content_types,
                                                                                    label=field.label,
                                                                                    required=field.required,
                                                                                    help_text=field.help_text)
        if not getattr(self, '_meta', None):
            return

        for generic_foreign_key in self._meta.model._meta.virtual_fields:
            if isinstance(generic_foreign_key, GenericForeignKey):
                initial = None
                old_content_type_field = self.fields[generic_foreign_key.ct_field]
                old_obj_id_field = self.fields[generic_foreign_key.fk_field]
                if not self.data:
                    initial = obj and getattr(obj, generic_foreign_key.name, None) or None
                else:
                    ct_id = self.data.get('%s_0' % generic_foreign_key.name, None)
                    fk_id = self.data.get('%s_1' % generic_foreign_key.name, None)
                    if ct_id and fk_id:
                        ctype = ContentType.objects.get(pk=ct_id)
                        initial = ctype.model_class().objects.get(pk=fk_id)
                cts_id = [ct.id for ct in old_content_type_field.queryset if not ct.model_class()]
                old_content_type_field.queryset = ContentType.objects.exclude(pk__in=cts_id)
                self.fields[generic_foreign_key.name] = self.generic_field(fields=[old_content_type_field, old_obj_id_field],
                                                                                    initial=initial,
                                                                                    filter_content_types=filter_content_types,
                                                                                    exclude_content_types=exclude_content_types,
                                                                                    label=old_content_type_field.label,
                                                                                    required=old_content_type_field.required or old_obj_id_field.required,
                                                                                    help_text=_('Select first the content type, and after select a content of this type'))
                del self.fields[generic_foreign_key.ct_field]
                del self.fields[generic_foreign_key.fk_field]

    def clean(self):
        cleaned_data = super(BaseGenericForm, self).clean()
        if not getattr(self, '_meta', None):
            return cleaned_data
        for generic_foreign_key in self._meta.model._meta.virtual_fields:
            if isinstance(generic_foreign_key, GenericForeignKey):
                obj = cleaned_data.get(generic_foreign_key.name, None)
                if not obj:
                    cleaned_data[generic_foreign_key.name] = None
                    cleaned_data[generic_foreign_key.ct_field] = None
                    cleaned_data[generic_foreign_key.fk_field] = None
                else:
                    cleaned_data[generic_foreign_key.ct_field] = ContentType.objects.get_for_model(obj)
                    cleaned_data[generic_foreign_key.fk_field] = obj.pk
        return cleaned_data


class GenericForm(BaseGenericForm):

    generic_field = GenericForeignKeyPublicField


class GenericAdminModelForm(BaseGenericForm, forms.ModelForm):

    generic_field = GenericForeignKeyAdminField
