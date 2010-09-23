from __future__ import absolute_import

import datetime
import logging
from operator import itemgetter

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site

from .util import ChoiceEnum
from . import settings as local_settings
try:
    from positions.fields import PositionField
except ImportError:
    logging.warn('positions not installed. '
                 'Will just use integers for position fields.')
    PositionField = None


class LiveEmailFormManager(models.Manager):

    def get_query_set(self):
        now = datetime.datetime.now()
        return super(LiveEmailFormManager, self).get_query_set().filter(
            is_published=True,
            starts_at__lte=now)


class EmailForm(models.Model):

    class Meta:
        ordering = ('-starts_at',)

    title = models.CharField(max_length=80)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    starts_at = models.DateTimeField(default=datetime.datetime.now)
    is_published = models.BooleanField(default=False)
    thanks_message = models.TextField(default=_("Thanks for entering!"))
    email = models.CharField(
        blank=True,
        help_text=_("Send a notification to this email whenever someone "
                   "submits an entry to this email form",),
        max_length=300)
    site = models.ForeignKey(Site)

    class Meta:
        unique_together = (('slug', 'site'),)

    def __unicode__(self):
        return self.title

    def get_url_path(self):
        kwargs={'slug' : self.slug}
        return reverse('emailform_detail',
                       kwargs=kwargs)

    def get_full_url(self):
        url = self.get_url_path()
        site = self.site or Site.objects.get_current()
        return 'http://%s%s' % (site.domain, url)

    def get_absolute_url(self):
        return self.get_full_url()

    objects = models.Manager()
    live = LiveEmailFormManager()

OPTION_TYPE_CHOICES = ChoiceEnum(sorted([('char', 'Text Field'),
                                         ('email', 'Email Field'),
                                         ('file', 'File Upload'),
                                         ('integer', 'Integer'),
                                         ('float', 'Float'),
                                         ('bool', 'Boolean'),
                                         ('text', 'Text Area'),
                                         ('select', 'Select One Choice'),
                                         ('radio', 'Radio List'),
                                         ('checkbox', 'Checkbox List'),
                                         ('zipcode', 'Zipcode'),
                                         ('usstate', 'US State'),
                                         ('phonenumber', 'Phone Number')],
                                        key=itemgetter(1)))


class Question(models.Model):

    class Meta:
        ordering = ('order',)

    emailform = models.ForeignKey(EmailForm, related_name="questions")
    question = models.TextField(help_text=_(
        "Appears on the email form entry page."))
    label = models.CharField(max_length=32, help_text=_(
        "Appears on the results page."))
    help_text = models.TextField(blank=True)
    required = models.BooleanField(default=False)
    if PositionField:
        order = PositionField(collection=('emailform',))
    else:
        order = models.IntegerField()
    option_type = models.CharField(max_length=12, choices=OPTION_TYPE_CHOICES)
    options = models.TextField(blank=True, default='')

    def __unicode(self):
        return self.question

    @property
    def parsed_options(self):
        if OPTION_TYPE_CHOICES.BOOLEAN == self.option_type:
            return [True, False]
        return filter(None, (s.strip() for s in self.options.splitlines()))


class Entry(models.Model):

    class Meta:
        verbose_name = "Entry"
        verbose_name_plural = "Entries"
        ordering = ('-submitted_at',)

    emailform = models.ForeignKey(EmailForm)
    ip_address = models.IPAddressField()
    submitted_at = models.DateTimeField(default=datetime.datetime.now)
    content = models.TextField(blank=True)
