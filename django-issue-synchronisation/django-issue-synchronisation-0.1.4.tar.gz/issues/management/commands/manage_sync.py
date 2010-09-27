# -*- coding: utf-8 -*-

"""Manage commands for issue trackers."""

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _

from issues.models import Tracker


class Command(BaseCommand):

    help = _(u'Administrative commands for django-issue-synchronisation.')

    option_list = BaseCommand.option_list + (
        make_option('--enable',
            action='store_true',
            dest='enable',
            default=False,
            help='Enable synchronisation for an issue tracker'),
        make_option('--disable',
            action='store_true',
            dest='disable',
            default=False,
            help='Disable synchronisation for an issue tracker'),
        )

    def handle(self, *args, **options):
        enabled = options.get('enable')
        disabled = options.get('disable')
        if enabled or disabled:
            disabled = not enabled
            if len(args) != 1:
                raise CommandError('No tracker id supported')
            tracker_id = args[0]
            tracker = Tracker.objects.filter(id=tracker_id)
            if not tracker:
                raise CommandError('No tracker found with id %s' % tracker_id)
            tracker = tracker[0]
            self.toggle_tracker(tracker, enabled)

    def toggle_tracker(self, tracker, value):
        tracker.active = value
        tracker.save()
