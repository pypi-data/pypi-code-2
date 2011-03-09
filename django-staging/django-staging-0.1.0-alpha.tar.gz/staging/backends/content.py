import os

from django.core import serializers
from django.db import models

from staging import settings

from staging.backends.base import StagingBackend


def get_fixtures(model_or_models):
    data = []
    if not isinstance(model_or_models, (list, tuple)):
        models_list = [model_or_models]
    else:
        models_list = model_or_models
    for model_item in models_list:
        queryset = model_item.objects.all()
        serialized_string = serializers.serialize('json', queryset, indent=2)
        data.append(serialized_string)
    return data


class ContentStagingBackend(StagingBackend):

    def _get_fixture_filename(self, app_label, model_name):
        return os.path.join(self.path, '%s_%s.xml' % (app_label, model_name))

    def export_to_staging(self):
        models_to_save = settings.STAGING_MODELS_TO_SAVE
        for app_label, model_name in models_to_save:
            model = models.get_model(app_label, model_name)
            fixtures = get_fixtures(model)
            fp = open(self._get_fixture_filename(app_label, model_name), 'w')
            fp.write("\n".join(fixtures))
            fp.close()

    def import_from_staging(self):
        models_to_save = settings.STAGING_MODELS_TO_SAVE
        for app_label, model_name in models_to_save:
            fp = open(self._get_fixture_filename(app_label, model_name))
            objects = serializers.deserialize('json', fp)
            for obj in objects:
                obj.save()
            fp.close()
