# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import base64
import pytz
import urllib
import urlparse

import grok
import zope.interface
import zope.component

import gocept.lms.interfaces


class URLContainer(grok.Container):

    zope.interface.implements(gocept.lms.interfaces.IURLProvider)

    def add(self, url_string):
        url = self.get_url(url_string)
        if url is None:
            url = URL(url_string)
            self[self.encode_url(url_string)] = url
        return url

    def get_url(self, url_string):
        return self.get(self.encode_url(url_string))

    @staticmethod
    def encode_url(url_string):
        return base64.urlsafe_b64encode(url_string)


class URL(grok.Model):

    zope.interface.implements(gocept.lms.interfaces.IURL)

    url = None
    state = None
    reason = None
    last_check = datetime.datetime.min.replace(tzinfo=pytz.UTC)
    last_state_change = datetime.datetime.min.replace(tzinfo=pytz.UTC)

    clients = gocept.reference.ReferenceCollection(ensure_integrity=True)

    def __init__(self, url_string):
        self.url = url_string
        self.clients = set()

    def __repr__(self):
        return "<%s.%s '%s'>" % (
            __name__, self.__class__.__name__, self.url)

    def __cmp__(self, other):
        if isinstance(other, URL):
            return cmp(self.url, other.url)
        return -1


class Purge(grok.View):

    grok.context(URL)

    def update(self):
        for client in self.context.clients:
            client.urls.remove(self.context)
        # After deletion we can't compute the application URL anymore so this
        # has to happen early.
        self.app_url = self.application_url()
        del self.context.__parent__[self.context.__name__]

    def render(self):
        self.redirect(self.app_url + '/urls')


@grok.adapter(str)
@grok.implementer(gocept.lms.interfaces.ISchemeHandler)
def get_handler(url):
    scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
    return zope.component.queryUtility(
        gocept.lms.interfaces.ISchemeHandler, name=scheme)
