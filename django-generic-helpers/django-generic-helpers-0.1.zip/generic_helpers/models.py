from django.db import models
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _
from generic_helpers.managers import GenericRelationManager, ContentType

class GenericRelationModel(models.Model):
    content_type = models.ForeignKey(ContentType,
        verbose_name = _('Content type'),
        related_name = 'content_type_set_for_%(class)s'
    )
    object_pk = models.TextField(
        verbose_name = _('Object ID'),
    )
    content_object = generic.GenericForeignKey(
        ct_field   = 'content_type',
        fk_field   = 'object_pk',        
    )
    objects = GenericRelationManager()

    class Meta:
        abstract = True