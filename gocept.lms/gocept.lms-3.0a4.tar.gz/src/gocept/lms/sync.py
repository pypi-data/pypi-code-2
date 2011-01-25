# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt
"""Perform daily synchronization of client databases."""

import datetime
import gocept.lms.interfaces
import grok
import logging
import pytz
import zope.component
import transaction

log = logging.getLogger(__name__)

INTERVAL = datetime.timedelta(seconds=24*3600)


class Synchronization(grok.Annotation, grok.Model):

    grok.provides(gocept.lms.interfaces.ISynchronization)
    grok.context(gocept.lms.interfaces.IClient)

    last = datetime.datetime.min.replace(tzinfo=pytz.UTC)
    force = False

    @property
    def client(self):
        return self.__parent__

    def sync(self):
        log.info('%s: performing synchronization' % self.client.id)
        log.info('%s: %s URLs currently registered' % (
            self.client.id, len(self.client.urls)))

        try:
            remote_urls = self.client.remote_urls()
        except Exception, e:
            log.exception(e)
            now = datetime.datetime.now(pytz.UTC)
            self.last = now
            self.force = False
            return

        # Make unique: we've seen clients submit the same URL multiple times
        # in one request.
        remote_urls = set(remote_urls)

        url_provider = zope.component.getUtility(gocept.lms.interfaces.IURLProvider)
        remote_urls = set(url_provider.add_multiple(remote_urls))

        log.info('%s: retrieved %s URLs' % (self.client.id, len(remote_urls)))

        local_urls = set(self.client.urls)

        # Step 1: Remove all URLs not known to the client anymore
        self.client.unregister_urls(local_urls-remote_urls)

        # Step 2: Add URLs that appeared at the client without registration
        self.client.register_urls(remote_urls-local_urls)
        log.info('%s: %s URLs remaining' % (
            self.client.id, len(self.client.urls)))

        # Step 3: Notify client about the status of all his URLs
        try:
            self.client.notify_all()
        except Exception, e:
            log.exception(e)
            now = datetime.datetime.now(pytz.UTC)
            self.last = now
            self.force = False
            return

        # Mark as updated
        notifications = gocept.lms.interfaces.INotifications(self.client)
        now = datetime.datetime.now(pytz.UTC)
        notifications.last = self.last = now
        self.force = False


def sync():
    reference_time = datetime.datetime.now(pytz.UTC) - INTERVAL

    clients = zope.component.getUtility(gocept.lms.interfaces.IClientProvider)
    for client in clients.values():
        notifications = gocept.lms.interfaces.INotifications(client)
        if not notifications.enabled:
            continue
        client_sync = gocept.lms.interfaces.ISynchronization(client)
        if client_sync.last > reference_time and not client_sync.force:
            continue
        client_sync.sync()
        transaction.commit()
