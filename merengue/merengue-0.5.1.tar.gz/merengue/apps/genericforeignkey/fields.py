from django import forms
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.forms.fields import IntegerField
from django.forms.models import ModelChoiceField

from genericforeignkey.widgets import GenericForeignKeyWidget, RelatedGenericPublicWidget, RelatedGenericAdminWidget


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
        self.widget = self.widget(widgets=[field_contenttype.widget, self.related_generic_widget], initial=initial)
        super(BaseGenericForeignKeyField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if len(data_list) == 2 and data_list[0] and data_list[1]:
            return data_list[0].model_class().objects.get(id=data_list[1])
        return None


class GenericForeignKeyAdminField(BaseGenericForeignKeyField, forms.MultiValueField):
    related_generic_widget = RelatedGenericAdminWidget


class GenericForeignKeyPublicField(BaseGenericForeignKeyField, forms.MultiValueField):
    related_generic_widget = RelatedGenericPublicWidget
