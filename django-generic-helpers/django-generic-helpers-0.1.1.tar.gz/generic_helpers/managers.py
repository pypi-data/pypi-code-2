from django.db import models
from django.contrib.contenttypes.models import ContentType

class GenericQuerySet(models.query.QuerySet):
    def get_for_object(self, object):
        return self.select_related().filter(
            content_type = ContentType.objects.get_for_model(object),
            object_pk    = object.pk,
        )

    def get_for_model(self, model):
        return self.select_related().filter(
            content_type=ContentType.objects.get_for_model(model)
        )

class GenericRelationManager(models.Manager):
    def get_query_set(self):
        return GenericQuerySet(self.model)

    def get_for_object(self, object):
        return self.get_query_set().select_related().\
            filter(
                content_type = ContentType.objects.get_for_model(object),
                object_pk    = object.pk,
            )
    def get_for_model(self, model):
        return self.get_query_set().select_related().\
            filter(content_type=ContentType.objects.get_for_model(model)
        )