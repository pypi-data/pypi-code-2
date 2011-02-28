# Copyright (C) 2010 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of linaro-django-jsonfield.
#
# linaro-django-jsonfield is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# linaro-django-jsonfield is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with linaro-django-jsonfield.  If not, see <http://www.gnu.org/licenses/>.

# XXX Lifted from http://code.djangoproject.com/ticket/12990

from django.conf import settings
from django.db import models
from django.db.models import signals
from django.utils import simplejson as json

from linaro_django_jsonfield.forms import JSONFormField


class JSONField(models.TextField):

    description = u"Data that serializes and deserializes into and out of JSON."

    def _dumps(self, data):
        return json.dumps(data)

    def _loads(self, str):
        return json.loads(str, encoding=settings.DEFAULT_CHARSET)

    def db_type(self):
        return 'text'

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname, None)
        return self._dumps(value)

    def contribute_to_class(self, cls, name):
        self.class_name = cls
        super(JSONField, self).contribute_to_class(cls, name)
        signals.post_init.connect(self.post_init)

        def get_json(model_instance):
            return self._dumps(getattr(model_instance, self.attname, None))
        setattr(cls, 'get_%s_json' % self.name, get_json)

        def set_json(model_instance, json):
            return setattr(model_instance, self.attname, self._loads(json))
        setattr(cls, 'set_%s_json' % self.name, set_json)

    def post_init(self, **kwargs):
        if 'sender' in kwargs and 'instance' in kwargs:
            if kwargs['sender'] == self.class_name and hasattr(kwargs['instance'], self.attname):
                value = self.value_from_object(kwargs['instance'])
                if isinstance(value, basestring):
                    value = self._loads(value)
                if (value):
                    setattr(kwargs['instance'], self.attname, value)
                else:
                    setattr(kwargs['instance'], self.attname, None)

    def formfield(self, **kwargs):
        return super(JSONField, self).formfield(form_class=JSONFormField, **kwargs)
