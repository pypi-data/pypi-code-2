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
from django.contrib.admin.widgets import AdminIntegerFieldWidget, RelatedFieldWidgetWrapper
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _


class GenericForeignKeyWidget(forms.MultiWidget):

    def __init__(self, widgets=None, initial=None, *args, **kwargs):
        self.initial = initial
        super(GenericForeignKeyWidget, self).__init__(widgets)
        [setattr(widget, 'genericforeignkey_initial', initial) for widget in self.widgets]

    def decompress(self, value):
        value = value or self.initial
        if value:
            ct = ContentType.objects.get(app_label=value._meta.app_label,
                                         model=value._meta.module_name)
            return [ct.id, value.id]
        return [None, None]


class BaseRelatedGenericWidget(object):

    class Media:
        js = ('%sgenericforeignkey/js/jquery.genericforeignkeywidget.js' % settings.MEDIA_URL, )
        css = {'all': ('%sgenericforeignkey/css/genericforeignkey.css' % settings.MEDIA_URL, )}

    def render(self, name, value, *args, **kwargs):
        output = u'<div style="float: left;" class="relatedgenericwidget">'
        output += u'<div style="padding-top: 3px; font-size:12px; line-height: 16px;">'
        output += u'<span class="selected_content hidden">'
        output += self.genericforeignkey_initial and smart_unicode(self.genericforeignkey_initial) or '----'
        output += u'</span>'
        output += u'<span class="remove_current">'
        output += u'<img src="%(media)sgenericforeignkey/img/cancel.png" alt="%(title)s" title="%(title)s" />' % {
            'title': _(u'Remove'),
            'media': settings.MEDIA_URL}
        output += u'</span>'
        output += u'</div>'
        output += u'<div class="obj_id">'
        output += super(BaseRelatedGenericWidget, self).render(name, value, *args, **kwargs)
        output += u'</div>'
        params=[]

        if params:
            params_str = '&id__in=%s' % ','.join(params)
        else:
            params_str = ''
        if getattr(self, 'genericforeignkey_initial', None):
            ct = ContentType.objects.get(app_label=self.genericforeignkey_initial._meta.app_label,
                                         model=self.genericforeignkey_initial._meta.module_name)
            params_str += '&content_type_id=%s' % ct.id

        output += self.get_related_generic_url(name, params_str)
        output += u'</div>'
        output += u'<br style="clear: left;" />'
        return mark_safe(u''.join(output))


class RelatedGenericPublicWidget(BaseRelatedGenericWidget, forms.TextInput):

    def _media(self):
        return forms.Media(js=('%sgenericforeignkey/js/jquery.genericforeignkeywidget.js' % settings.MEDIA_URL,
                               '%sgenericforeignkey/js/genericforeignkeywidget_public.js' % settings.MEDIA_URL,
                               reverse('django.views.i18n.javascript_catalog'), ),
                           css = {'all': ('%sgenericforeignkey/css/genericforeignkey.css' % settings.MEDIA_URL, )})
    media = property(_media)

    def get_related_generic_url(self, name, params_str):
        return u'<a id="lookup_id_%s" class="content_type hidden" href="%s?%s">%s</a>' % (name, reverse('generic_object_list'), params_str, _('Select content'))


class RelatedGenericAdminWidget(BaseRelatedGenericWidget, AdminIntegerFieldWidget):

    def get_related_generic_url(self, name, params_str):
        return u'<a id="lookup_id_%s" class="content_type hidden" href="/admin/contenttypes/contenttype/?%s" onclick="javascript:showRelatedObjectLookupPopup(this); return false;">%s</a>' % (name, params_str, _('Select content'))


class RelatedFieldWidgetWrapperWithOutAddLink(RelatedFieldWidgetWrapper):

    def render(self, name, value, *args, **kwargs):
        rel_to = self.rel.to
        info = (rel_to._meta.app_label, rel_to._meta.object_name.lower())
        self.widget.choices = self.choices
        output = [self.widget.render(name, value, *args, **kwargs)]
        return mark_safe(u''.join(output))
