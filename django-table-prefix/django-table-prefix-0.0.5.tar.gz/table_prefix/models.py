from django.db import models
from table_prefix.utils import get_table_name, models_is_prefixed


for app in models.get_apps():
    app_name = app.__name__.split('.')[-2]
    model_list = models.get_models(app)
    for model in model_list:
        model_path = ".".join((model._meta.app_label,
                               model._meta.object_name))
        if models_is_prefixed(model):
            model._meta.db_table = get_table_name(model._meta.db_table)
