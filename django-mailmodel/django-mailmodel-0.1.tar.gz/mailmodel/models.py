#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

class MailModel(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    recipient_name = models.CharField(max_length=150, null=True)
    recipient_email = models.EmailField()
    body = models.TextField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType,
                    verbose_name=_('content type'),
                    related_name="content_type_set_for_%(class)s")
    object_pk = models.TextField(_('object ID'))
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")
    
    def __unicode__(self):
        return "form %s to %" % (self.email, self.recipient_email)