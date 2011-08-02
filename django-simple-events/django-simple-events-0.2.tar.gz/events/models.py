from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _
from django.conf import settings

from itertools import islice, takewhile
from datetime import datetime
from dateutil import rrule

frecuencies = (
        (-1, _('Single time')),
        (rrule.DAILY, _('Daily')),
        (rrule.WEEKLY, _('Weekly')),
        (rrule.MONTHLY, _('Montly')),
        (rrule.YEARLY, _('Yearly')), 
        )

MAX_PAST = getattr(settings, 'EVENTS_MAX_PAST_OCCURRENCES', None)
MAX_FUTURE = settings.EVENTS_MAX_FUTURE_OCCURRENCES

class Occurrency(models.Model):
    datetime = models.DateTimeField()
    event = models.ForeignKey('Event')

    def __unicode__(self):
        return unicode(self.datetime)


class Event(models.Model):
    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')

    beginning = models.DateField(_('Beginning'))
    time = models.TimeField(_('Time'))
    duration = models.TimeField(_('Duration'))

    frecuency = models.SmallIntegerField(_('Frecuency'), choices=frecuencies, 
            default=-1)

    interval = models.PositiveSmallIntegerField(_('Interval'), default=1, 
            help_text=_('Interval between frecuencies'))

    repetitions = models.PositiveSmallIntegerField(_('Maximum repetitions'), 
            blank=True, null=True, help_text=_('Endless if not defined'))

    end = models.DateTimeField(_('Maximum date'), blank=True, null=True, 
            help_text=_('Endless if not defined'))


    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return '%s %s %s' % (unicode(self.beginning), unicode(self.time),
                self.get_frecuency_display())

    def get_occurrences(self):
        if self.frecuency is -1:
            return datetime.combine(self.beginning, self.time),
        return rrule.rrule(
                self.frecuency, 
                dtstart=datetime.combine(self.beginning, self.time),
                interval=self.interval,
                count=self.repetitions,
                until=self.end,
                )

    def get_past_occurrences(self, num=None):
        past = list(takewhile(
            lambda ocurrency: ocurrency < datetime.now(),
            self.get_occurrences(),
            ))
        if num:
            return past[:-num:-1]
        return past[::-1]

    def get_future_occurrences(self, num):
        future = ( ocurrency for ocurrency in self.get_occurrences()\
                if ocurrency > datetime.now() )
        return list(islice(future, None, num))

    def update_occurrences(self, occurrences):
        #delete old ones
        for occurrency in self.occurrency_set.exclude(datetime__in=occurrences):
            occurrency.delete()
        #add new ones
        for occurrency in occurrences:
            if not self.occurrency_set.filter(datetime=occurrency):
                Occurrency(datetime=occurrency, event=self).save()

    def save(self, *args, **kwargs):
        if self.repetitions or self.end:
            occurrences = self.get_ocurrences()
        else:
            occurrences = self.get_past_occurrences(MAX_PAST) +\
                    self.get_future_occurrences(MAX_FUTURE)

        super(Event, self).save(*args, **kwargs)
        self.update_occurrences(occurrences)

    def delete(self, *args, **kwargs):
        for occurrency in self.occurrency_set.all():
            occurrency.delete()
        super(Event, self).delete(*args, **kwargs)
