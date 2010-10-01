# -*- coding: utf-8 -*-

"""Synchronisation command."""

from optparse import make_option
import os
import sys
import time

from django.core.management.base import BaseCommand
from django.db.models import get_models
from django.utils.translation import ugettext as _

from issues import hooks
from issues.models import Tracker
from issues.plugin import PluginManager


PLUGINS = PluginManager()
PLUGINS.add_directory(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                   '../../backends')))
PLUGINS.rescan_directories()


class Command(BaseCommand):

    help = _(u'Synchronizes one or many issue tracker.')

    option_list = BaseCommand.option_list + (
        make_option('--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Test the synchronisation but don\'t make changes'),
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run')
        hooks.initialize()
        ids = []
        print args, options
        for id in args:
            ids.append(id)
        if ids:
            query = Tracker.objects.filter(id__in=ids)
        else:
            query = Tracker.objects.all()
        query = query.order_by('id')
        for tracker in query:
            retval = self.run(tracker)

    def run(self, tracker):
        self.stdout.write('Loading issue tracker \'%s\'\n' % tracker)
        if not tracker.active:
            self.stdout.write('Skipping (deactivated)\n')
            return True
        a = time.time()
        backend = PLUGINS.by_id(tracker.type.cid)
        retval = backend.sync(tracker)
        b = time.time()
        self.stdout.write('Syncing took %s second(s)\n' % round(b-a, 3))
        return retval
