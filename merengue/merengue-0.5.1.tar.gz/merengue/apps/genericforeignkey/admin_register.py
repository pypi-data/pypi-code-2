try:
    from threading import local
    from merengue.base.admin import BaseAdmin
except ImportError:
    from django.contrib.admin import ModelAdmin as BaseAdmin
    from django.utils._threading_local import local
from django.contrib.contenttypes.models import ContentType
from genericforeignkey.utils import get_objects_of_content_type


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

    def changelist_view(self, request, extra_context=None):
        extra_context = self._base_update_extra_context(extra_context)
        content_type_id = request.GET.get('content_type_id', None)
        if content_type_id:
            content_type = ContentType.objects.get(pk=content_type_id)
            self.model = content_type.model_class()
        else:
            self.model = ContentType
        return super(GenericContentTypeAdmin, self).changelist_view(request, extra_context)

    def queryset(self, request):
        content_type_id = request.GET.get('content_type_id', None)
        if content_type_id:
            return get_objects_of_content_type(request, content_type_id)
        return super(GenericContentTypeAdmin, self).queryset(request)
