# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import logging
import os
import pprint
import decorator

import transaction
import BTrees
import grok
import zc.catalog.catalogindex
import zc.queue
import zc.queue.interfaces
import zope.app.catalog.catalog
import zope.app.catalog.field
import zope.app.catalog.interfaces
import zope.app.intid
import zope.app.intid.interfaces
import zope.component
import zope.security.interfaces

import gocept.lms.interfaces
import gocept.lms.url
import gocept.lms.client

log = logging.getLogger(__name__)

PROTOCOL_VERSION = 2


def setup_url_catalog(catalog):
    catalog['state'] = zope.app.catalog.field.FieldIndex(
        'state', gocept.lms.interfaces.IURL)
    catalog['last_check'] = zope.app.catalog.field.FieldIndex(
        'last_check', gocept.lms.interfaces.IURL)
    catalog['last_state_change'] = zope.app.catalog.field.FieldIndex(
        'last_state_change', gocept.lms.interfaces.IURL)
    catalog['clients'] = zc.catalog.catalogindex.SetIndex(
        'clients', gocept.lms.interfaces.IURL)


class LMS(grok.Application, grok.Container):

    grok.local_utility(gocept.lms.url.URLContainer,
                       provides=gocept.lms.interfaces.IURLProvider,
                       public=True)

    grok.local_utility(gocept.lms.client.ClientContainer,
                       provides=gocept.lms.interfaces.IClientProvider,
                       public=True)

    grok.local_utility(zope.app.intid.IntIds,
                       provides=zope.app.intid.interfaces.IIntIds)

    grok.local_utility(zope.app.catalog.catalog.Catalog,
                       provides=zope.app.catalog.interfaces.ICatalog,
                       setup=setup_url_catalog,
                       name='urls')

    grok.local_utility(zc.queue.CompositeQueue,
                       provides=zc.queue.interfaces.IQueue,
                       name='check')


class Index(grok.View):
    pass # see app_templates/index.pt


class Alerts(grok.View):
    pass # see app_templates/alerts.pt


class URLs(grok.View):

    def update(self, pattern=None):
        self.pattern = pattern

    def urls(self):
        if not self.pattern:
            return
        urls = zope.component.getUtility(gocept.lms.interfaces.IURLProvider)
        for url in urls.values():
            if self.pattern in url.url:
                yield url


@decorator.decorator
def authenticatedClient(method, self, client_id, password, *args, **kwargs):
    """Make sure the client is authenticated and pass the client object to
    method.

    """
    clients = zope.component.getUtility(
        gocept.lms.interfaces.IClientProvider)
    client = clients.get(client_id)
    if client is None or client.password != password:
        raise zope.security.interfaces.Unauthorized
    return method(self, client, password, *args, **kwargs)

@decorator.decorator
def logged(method, self, *args):
    args_str = pprint.pformat(args)
    note = (u'XML-RPC: %s.%s\n%s' % (
        self.__class__.__name__, method.__name__, args_str))[:1000]
    transaction.get().note(note.encode('utf8'))
    log.info('%s: %s' % (self.request.principal.title, note.encode('utf-8')))
    result = method(self, *args)
    if not transaction.get().description:
        # if transaction note got lost, set it here again
        transaction.get().note(note.encode('utf8'))
    note = note + u'\nResult: %s' % result
    log.debug('%s: %s' % (self.request.principal.title, note.encode('utf-8')))
    return result


class XMLRPC(grok.XMLRPC):

    def registerClient(self, secret, id, callback,
                       contact_name, contact_email):
        client = gocept.lms.client.Client(id)
        client.callback = callback
        client.contact_name = contact_name
        client.contact_email = contact_email
        client.password = os.urandom(24).encode('base64')[:-3]
        clients = zope.component.getUtility(
            gocept.lms.interfaces.IClientProvider)
        clients.add(client)
        return True

    @logged
    @authenticatedClient
    def checkConnection(self, client, password):
        return PROTOCOL_VERSION

    @logged
    @authenticatedClient
    def getClientNotifications(self, client, password):
        return gocept.lms.interfaces.INotifications(client).enabled

    @logged
    @authenticatedClient
    def setClientNotifications(self, client, password, status):
        gocept.lms.interfaces.INotifications(client).enabled = bool(status)

    @logged
    @authenticatedClient
    def registerURLs(self, client, password, urls):
        url_objects = list(self.url_provider.add_multiple(urls))
        client.register_urls(url_objects)
        result = [(url.url, url.state, url.reason)
                  for url in url_objects
                  if url.state is not None]
        return result

    @logged
    @authenticatedClient
    def unregisterURLs(self, client, password, urls):
        url_objects = (url for url in
                       (self.url_provider.get_url(url) for url in urls)
                       if url is not None)
        client.unregister_urls(url_objects)
        return True

    @logged
    @authenticatedClient
    def forceSynchronization(self, client, password):
        sync = gocept.lms.interfaces.ISynchronization(client)
        sync.force = True

    @logged
    def getInfoFrameURL(self, client_id, password):
        # XXX API stub
        return 'http://lms.gocept.com/v2/alerts'

    # XXX missing
    # listClients(admin_secret)


    @property
    def url_provider(self):
        return zope.component.getUtility(gocept.lms.interfaces.IURLProvider)
