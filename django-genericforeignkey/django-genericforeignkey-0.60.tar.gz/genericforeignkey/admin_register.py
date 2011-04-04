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
try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

try:
    from merengue.base.admin import BaseAdmin
    from merengue.base.adminsite import site
except ImportError:
    from django.contrib.admin import site
    from django.contrib.admin import ModelAdmin as BaseAdmin

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied

from genericforeignkey.utils import clear_content_type, get_objects_of_content_type


_thread_locals = local()


def get_current_model():
    return getattr(_thread_locals, "model", ContentType)


def set_current_model(model):
    _thread_locals.model = model
    return model


class GenericContentTypeAdmin(BaseAdmin):

    list_display = ('__unicode__', )
    generic_fields = ["object"]

    def _get_model(self):
        return get_current_model()

    def _set_model(self, model):
        return set_current_model(model)

    model = property(_get_model, _set_model)

    class Media:
        js = ("genericforeignkey/js/content_type_object.js", )

    def search_modeladmin(self):
        for model in self.model.mro():
            if model in site._registry:
                return site._registry[model]
        return None

    def changelist_view(self, request, extra_context=None):
        extra_context = self._base_update_extra_context(extra_context) or {}
        content_type_id = request.GET.get('content_type_id', None)
        if content_type_id:
            content_type = ContentType.objects.get(pk=content_type_id)
            self.model = content_type.model_class()
            if settings.SEARCH_MODELADMIN:
                model_admin = self.search_modeladmin()
                if model_admin:
                    clear_content_type(request)
                    extra_context['search_mode'] = True
                    extra_context['generic_fk_media'] = self.media
                    return model_admin.changelist_view(request, extra_context)
        else:
            self.model = ContentType
        return super(GenericContentTypeAdmin, self).changelist_view(request, extra_context)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        raise PermissionDenied

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def queryset(self, request):
        content_type_id = request.GET.get('content_type_id', None)
        if content_type_id:
            return get_objects_of_content_type(request, content_type_id)
        return super(GenericContentTypeAdmin, self).queryset(request)
