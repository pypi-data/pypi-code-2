from django.contrib.contenttypes.models import ContentType
from django.db.models import get_model
from yama.settings import MODELS

def get_content_types():
    return  [
                ContentType.objects.get(
                    app_label=app,
                    model=model.lower,
                ).pk
                for (app, model) in MODELS.keys()
            ]

def get_queryset(request, content_type):
    opts = content_type._meta
    app_label = opts.app_label
    model_name = opts.object_name
    q_object = MODELS[(app_label, model_name)]
    if callable(q_object):
        q_object = q_object(request)
    return content_type._default_manager.filter(q_object)
