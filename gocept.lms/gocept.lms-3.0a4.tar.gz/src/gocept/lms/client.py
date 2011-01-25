# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import xmlrpclib
import logging

import pytz
import BTrees
import grok
import grokcore.formlib.formlib
from hurry.query import Ge
from hurry.query.set import AnyOf
import hurry.query.interfaces
import zope.interface
import zope.component
import zope.event
import zope.lifecycleevent
import gocept.reference

import gocept.lms.interfaces

log = logging.getLogger(__name__)

# Provide hook for tests to set up dummies
ServerProxy = xmlrpclib.ServerProxy


class ClientContainer(grok.Container):

    zope.interface.implements(gocept.lms.interfaces.IClientProvider)

    def add(self, client):
        self[client.id] = client


class Client(grok.Model):

    zope.interface.implements(gocept.lms.interfaces.IClient)

    id = None
    password = None
    contact_name = None
    contact_email = None
    callback = None

    urls = gocept.reference.ReferenceCollection(ensure_integrity=True)

    def __init__(self, id):
        self.id = id
        # This isn't a real set. It gets turned into something else by
        # gocept.relation.
        self.urls = set()

    def __cmp__(self, other):
        if isinstance(other, Client):
            return cmp(self.id, other.id)
        return -1

    def register_urls(self, urls):
        to_add = set(urls).difference(self.urls)
        for url in to_add:
            self.urls.add(url)
            url.clients.add(self)
            zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(url))

    def unregister_urls(self, urls):
        to_remove = set(urls).intersection(self.urls)
        for url in to_remove:
            self.urls.remove(url)
            url.clients.remove(self)
            zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(url))

    def iter_urls(self):
        return iter(self.urls)

    def remote_urls(self):
        """Get all URLs from the remote client."""
        return self.rpc.xmlrpc_getAllLinks(self.id, self.password)

    def notify_all(self):
        """Send notifications for all URLs of this client."""
        self.notify(self.urls)

    def notify_update(self):
        """Send notifications for all URLS of this client
        that had a status change since INotifications.last.

        """
        notifications = gocept.lms.interfaces.INotifications(self)
        url_query = zope.component.getUtility(hurry.query.interfaces.IQuery)
        urls = url_query.searchResults(
            Ge(('urls', 'last_state_change'), notifications.last) &
            AnyOf(('urls', 'clients'), [self]))
        if not urls:
            # No URLs have changed since last time. Nothing to do.
            return
        self.notify(urls)

    def notify(self, urls):
        """Send notifications about given urls."""
        log.info('Notifying client %s about URLs: %r' % (self.id, urls))
        notifications = [(url.url,
                          url.state or 'unknown', url.reason or 'unknown')
                         for url in urls]
        self.rpc.updateManyStates(self.id, self.password, notifications)

    @property
    def rpc(self):
        return ServerProxy(self.callback)


class NotificationsDisabled(object):
    """Event that signals that the notifications for a client where
    disabled.
    """

    def __init__(self, client):
        self.client = client


class Notifications(grok.Annotation, grok.Model):

    grok.provides(gocept.lms.interfaces.INotifications)
    grok.context(gocept.lms.interfaces.IClient)

    enabled = True
    last = datetime.datetime.min.replace(tzinfo=pytz.UTC)
    failed = 0

    def _p_resolveConflict(c, oldState, savedState, newState):
        # This usually happens with updating `last`. We're being
        # gracious about the other values.
        savedState['last'] = newState.get('last', c.last)
        savedState['enabled'] = (savedState.get('enabled', c.enabled) or
                                 newState.get('enabled', c.enabled))
        savedState['failed'] = min(savedState.get('failed', c.failed),
                                   newState.get('failed', c.failed))
        return savedState

    def notify(self):
        """Perform notifications on the recipient."""
        try:
            self.__parent__.notify_update()
        except Exception, e:
            log.exception(e)
            self.failed += 1
            if self.failed >= 20:
                log.warn('Disabling notifications for client %s due to too '
                         'many failed attempts.' % self.__parent__.id)
                self.enabled = False
                zope.event.notify(
                    gocept.lms.client.NotificationsDisabled(self.__parent__))
        else:
            self.failed = 0
            self.last = datetime.datetime.now(pytz.UTC)


class AddClient(grok.AddForm):
    """Register a new client."""

    grok.context(ClientContainer)
    grok.require('zope.ManageApplication')

    form_fields = grok.AutoFields(gocept.lms.interfaces.IClient)

    @grok.action('Add')
    def add(self, **data):
        client = Client(data['id'])
        grokcore.formlib.formlib.apply_data(client, self.form_fields, data)
        self.context.add(client)
