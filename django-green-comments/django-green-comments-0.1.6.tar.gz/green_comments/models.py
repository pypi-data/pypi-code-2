# -*- coding: utf-8 -*-
from datetime import datetime
import markdown

from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import linebreaks
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf import settings

from common.html import urlize

class Comment(models.Model):
    user = models.ForeignKey(User, related_name='comments')
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children')

    created = models.DateTimeField()
    updated = models.DateTimeField(blank=True, default=datetime.now)
    is_deleted = models.BooleanField(blank=True, default=False)

    content = models.TextField(u'Сообщение')
    content_html = models.TextField()

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

    def __unicode__(self):
        return 'Comment #%d [%s...]' % (self.pk, self.content[:100])

    def save(self, *args, **kwargs):
        if not self.created:
            self.created = datetime.now()
        if settings.COMMENTS_RENDER_METHOD == 'text':
            self.content_html = urlize(linebreaks(self.content)) 
        elif settings.COMMENTS_RENDER_METHOD == 'markdown':
            self.content_html = urlize(markdown.markdown(
                self.content, safe_mode='escape')) 
        else:
            raise Exception('Unknown render method')
        super(Comment, self).save(*args, **kwargs)

    def iter_children(self):
        for child in self.children.all():
            for subchild in child.iter_children():
                yield subchild
            yield child

    def iter_parents(self):
        obj = self
        while obj.parent_id:
            yield obj.parent
            obj = obj.parent

    def get_absolute_url(self):
        return self.content_object.get_absolute_url() + '#comment-%d' % self.pk
