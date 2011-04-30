from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

loglevels = (
             ('info', 'info'),
             ('debug', 'debug'),
             ('warning', 'warning'),
             ('error', 'error'),
             ('critical', 'critical'),
             ('exception', 'exception')
             )

class LogEntry(models.Model):
    loglevel = models.CharField(max_length = 20, default = 'information', choices=loglevels)
    date_added = models.DateTimeField(auto_now = True)
    text = models.TextField()
    context_name = models.CharField(max_length = 50, default = 'general', null = True, blank = True)
    user =  models.ForeignKey(User, null = True, blank = True, related_name='log_entries')
    content_type =  models.ForeignKey(ContentType, null = True, blank = True, related_name='log_entries')
    object_id = models.PositiveIntegerField(null = True, blank = True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-date_added']
        get_latest_by = 'date_added'
        verbose_name = 'Log entry'
        verbose_name_plural = 'Log entries'

    def __unicode__(self):
        return "%s [%s] - %s : %s Instance: %s." % \
            (self.date_added, self.loglevel, \
             self.user and "@%s" % self.user or '', \
                 len(self.text) > 100 and "%s ..." % \
                     self.text[0:100] or self.text, \
                     self.context_name and 'Yes' or 'No')

    def view_details(self):
        return '<a href="%s">Details</a>' % reverse('avocado-details', args=[self.id])
    view_details.short_description = 'View logging details'
    view_details.allow_tags = True

    def short_text(self):
        if len(self.text) < 100:
            return self.text
        return "%s ..." % self.text[0:100]
    short_text.short_description = 'Text'
    short_text.allow_tags = True

    def user_text(self):
        if self.user:
            return self.user
        return ""
    user_text.short_description = 'Related user'
    user_text.allow_tags = True
    
    def content_link(self):
        if not self.content_object:
            return ''
        return '<a href="%s">%s</a>' % \
            (reverse('admin:%s_%s_change' % (self.content_type.app_label, \
                                            self.content_type.model), args=[self.object_id]), \
             self.content_object)
    content_link.short_description = 'Link to content_object'
    content_link.allow_tags = True
