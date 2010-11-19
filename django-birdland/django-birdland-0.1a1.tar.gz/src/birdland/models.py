import datetime

from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from django.utils.dateformat import format
from django.contrib.auth.models import User
from django.dispatch import dispatcher

from birdland import managers, signals
from birdland.conf import settings
from birdland.markup import get_markups

if settings.TAGGING_ENABLED:
    import tagging.fields

class Entry(models.Model):
    """
    A weblog entry.
    """

    DRAFT_STATUS, PUBLISH_STATUS, REMOVED_STATUS = 1, 2, 3

    STATUS_CHOICES = (
        (DRAFT_STATUS, _('Draft')),
        (PUBLISH_STATUS, _('Publish')),
        (REMOVED_STATUS, _('Removed')),
    )

    # Metadata Fields
    
    author = models.ForeignKey(User, verbose_name=_('author'), related_name='entries')
    title = models.CharField(_('title'), max_length=256)
    slug = models.SlugField(_('slug'), max_length=64)
    created = models.DateTimeField(
        _('created on'),
        default=datetime.datetime.now, editable=False
    )
    modified = models.DateTimeField(
        _('last modified on'),
        editable=False
    )
    publish = models.DateTimeField(
        _('publish on'),
        default=datetime.datetime.now
    )
    status = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=DRAFT_STATUS)

    if settings.TAGGING_ENABLED:
        tags = tagging.fields.TagField(verbose_name=_('tags'))
    if settings.BACKLINKS_ENABLED:
        backlinks_enabled = models.BooleanField(_('backlinks enabled'), default=True)

    # Content Fields

    summary_markup = models.CharField(
        _('summary markup language'),
        max_length=10,
        choices=[(value, display) for value, display, callback in get_markups()],
        default=settings.DEFAULT_MARKUP_LANG
    )
    summary = models.CharField(_('summary'), max_length=1024, blank=True)
    summary_html = models.TextField(_('summary html'),
                                    blank=True, editable=False)

    body_markup = models.CharField(
        _('body markup language'),
        max_length=10,
        choices=[(value, display) for value, display, callback in get_markups()],
        default=settings.DEFAULT_MARKUP_LANG
    )
    body = models.TextField(_('body text'), blank=True)
    body_html = models.TextField(_('body html'), blank=True, editable=False)

    # Managers

    objects = managers.EntryManager()

    class Meta:
        verbose_name = _('entry')
        verbose_name_plural = _('entries')
        ordering = ['-publish',]
        get_latest_by = 'publish'

    # Methods

    def __unicode__(self):
        return self.title

    def save(self, **kwargs):
        # Process the markup, adding signal hooks for any additional processing
        # before and after the default markup processing behavior
        self.modified = datetime.datetime.now()
        signals.entry_markup_preprocess.send(sender=self)
        for markup, title, formatter in get_markups():
            if self.summary_markup == markup:
                self.summary_html = formatter(self.summary)
            if self.body_markup == markup:
                self.body_html = formatter(self.body)
        signals.entry_markup_processed.send(sender=self)
        super(Entry, self).save(**kwargs)

    def get_absolute_url(self):
        return ('birdland.views.public.entry_archive_detail', (),
                {'year': format(self.publish, 'Y'),
                 'month': format(self.publish, 'b'),
                 'day': format(self.publish, 'd'),
                 'slug': self.slug})
    get_absolute_url = permalink(get_absolute_url)

    def _next_previous_helper(self, direction):
        return getattr(self, 'get_%s_by_publish' % direction)(
            status__exact=self.PUBLISH_STATUS,
            publish__lte=datetime.datetime.now())

    def next_entry(self):
        return self._next_previous_helper('next')

    def previous_entry(self):
        return self._next_previous_helper('previous')
