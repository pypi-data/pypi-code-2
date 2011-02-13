# Copyright (c) 2008-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import base64
import datetime
import gocept.lms.interfaces
import grok
import pytz
import urllib
import urlparse
import zope.component
import zope.interface
import zope.schema.interfaces


def prepare_urls(urls):
    """Take a list of URL strings and ensure they're valid URLs
    for the LMS.

    This method is a convenience to filter out invalid URL strings and
    may thus return a list that is shorter than the list passed in.

    """
    for url in urls:

        yield url


class URLContainer(grok.Container):

    zope.interface.implements(gocept.lms.interfaces.IURLProvider)

    def add(self, url_string):
        url_string = gocept.lms.interfaces.IURL['url'].fromUnicode(url_string)
        url = self.get_url(url_string)
        if url is None:
            url = URL(url_string)
            self[self.encode_url(url_string)] = url
        return url

    def add_multiple(self, urls):
        for url in urls:
            try:
                obj = self.add(url)
            except (UnicodeEncodeError, UnicodeDecodeError,
                    zope.schema.interfaces.InvalidURI):
                continue
            yield obj

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

    def update_check(self, state, when, reason):
        self.last_check = when
        if state != self.state:
            self.last_state_change = when
            self.state = state
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(self))

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
