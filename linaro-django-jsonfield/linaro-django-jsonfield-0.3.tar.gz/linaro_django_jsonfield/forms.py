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
# XXX Lifted from: http://www.davidcramer.net/code/448/cleaning-up-with-json-and-sql.html

from django import forms
from django.core.exceptions import ValidationError
from django.utils import simplejson as json


class JSONWidget(forms.Textarea):

    def render(self, name, value, attrs=None):
        if not isinstance(value, basestring):
            value = json.dumps(value, indent=4)
        return super(JSONWidget, self).render(name, value, attrs)


class JSONFormField(forms.CharField):

    def __init__(self, *args, **kwargs):
        kwargs['widget'] = JSONWidget
        super(JSONFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        if not value:
            return
        try:
            return json.loads(value)
        except Exception, exc:
            raise forms.ValidationError(u'JSON decode error: %s' % (unicode(exc),))
