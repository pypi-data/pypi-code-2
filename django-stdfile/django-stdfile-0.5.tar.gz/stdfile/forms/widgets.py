# Copyright (c) 2010 by Yaco Sistemas <pmartin@yaco.es>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _


class DeleteCheckboxWidget(forms.CheckboxInput):

    def __init__(self, *args, **kwargs):
        self.is_image = kwargs.pop('is_image')
        self.value = kwargs.pop('initial')
        super(DeleteCheckboxWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        value = value or self.value
        if value:
            s = u'<table style="border-style:none;margin-left:9em;" class="DeleteCheckboxWidget">'
            s += u'<tr><td style="vertical-align: middle;">%s:</td>' % _('Currently')
            if self.is_image:
                s += u'<td><img src="%s%s" width="50"></td></tr>' % (settings.MEDIA_URL, value)
            elif getattr(value, 'url', None):
                s += u'<td><a href="%s%s">%s</a></td></tr>' % (settings.MEDIA_URL, value, value.url)
            else:
                s += u'<td>%s</td></tr>' % _('If you want to see the old file refresh the page. Do not press F5')
            s += u'<tr><td style="vertical-align: middle;">%s:</td><td>%s</td>' % (_('Delete'), super(DeleteCheckboxWidget, self).render(name, False, attrs))
            s += u'</table>'
            return s
        else:
            return u''


class RemovableFileFormWidget(forms.MultiWidget):

    def __init__(self, is_image=False, initial=None, **kwargs):
        widgets = (forms.FileInput(), DeleteCheckboxWidget(is_image=is_image, initial=initial))
        super(RemovableFileFormWidget, self).__init__(widgets)

    def decompress(self, value):
        return [None, value]
