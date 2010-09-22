# -*- coding: utf-8 -*-

import logging
import os
import sys

from django.core.management.base import BaseCommand
from django.db.models import get_models
from django.utils.translation import ugettext as _

from issues import hooks
from issues.models import Tracker
from issues.plugin import PluginManager

log = logging.getLogger(__name__)


PLUGINS = PluginManager()
PLUGINS.add_directory(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                   '../../backends')))
PLUGINS.rescan_directories()


def run(tracker):
    if tracker.active:
        import time
        a = time.time()
        backend = PLUGINS.by_id(tracker.type.cid)
        backend.sync(tracker)
        b = time.time()
        print 'Syncing took %s second(s).' % round(b-a, 3)
    #try:

        #return True
    #except:
        #return False


class Command(BaseCommand):

    help = _(u'Synchronizes one or many issue tracker.')

    def handle(self, *args, **options):
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
            run(tracker)
