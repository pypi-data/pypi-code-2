# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.interface
import zope.schema
import z3c.schema.email
import zc.sourcefactory.basic


STATE_OK = 'ok'
STATE_TEMPORARY = 'temporary unavailable'
STATE_UNAVAILABLE = 'unavailable'
STATE_CANT_CHECK = 'unsupported protocol'


class StateSource(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        return STATE_OK, STATE_TEMPORARY, STATE_UNAVAILABLE, STATE_CANT_CHECK


class IURLProvider(zope.interface.Interface):
    """URL container."""

    # XXX find a better name for this interface

    def add(url_string):
        """Create a new URL object and store it.

        Returns the new URL object. If an object representing the URL already
        exists, that object is returned.

        """

    def get_url(url_string):
        """Retrieve the URL object stored for the given URL.

        If no object for the given URL has been stored, None is returned.

        """


class IURL(zope.interface.Interface):

    url = zope.schema.URI(
        title=u'URL') # XXX make unique

    state = zope.schema.Choice(
        title=u'State',
        source=StateSource(),
        required=False)

    reason = zope.schema.TextLine(
        title=u'Reason for state',
        required=False)

    last_check = zope.schema.Datetime(
        title=u'Last checked',
        required=False)

    last_state_change = zope.schema.Datetime(
        title=u'State last changed',
        required=False)

    clients = zope.interface.Attribute(
        u'Iterable of all clients that registered this URL.')


class IClientProvider(zope.interface.Interface):
    """Client container."""

    # XXX find a better name for this interface

    def add(client):
        """Store a client object under its Id."""

    def __getitem__(id):
        """Retrieve a Client object by Id."""

    def get(id, default=None):
        """Retrieve a Client object by Id."""


class INotifications(zope.interface.Interface):
    """Manage notifications for a recipient."""

    enabled = zope.schema.Bool(
        title=u'Notify?',
        default=True)

    last = zope.schema.Datetime(
        title=u'Last notified')

    failed = zope.schema.Int(
        title=u'Number of failed notifications',
        default=0)

    def notify():
        """Perform notifications on the recipient."""


class IClient(zope.interface.Interface):

    id = zope.schema.TextLine(
        title=u'Client Id',
        description=u'Id used for authentication.') # XXX make unique

    password = zope.schema.Password(
        title=u'Password')

    contact_name = zope.schema.TextLine(
        title=u'Contact name',
        description=u'Real name of the person.')

    contact_email = z3c.schema.email.RFC822MailAddress(
        title=u'Contact email address')

    callback = zope.schema.URI(
        title=u'Callback URL')

    def iter_urls():
        """Return an iterable of the URLs registered for the client."""

    def remote_urls():
        """Get all URLs from the remote client."""

    def register_urls(urls):
        """Register URLs for client.

        urls: an iterable of IURL objects

        """

    def unregister_urls(urls):
        """Unregister URLs for client.

        urls: an iterable of IURL objects

        """

    def notify_all():
        """Send notifications for all URLs of this client."""

    def notify_update():
        """Send notifications for all URLS of this client
        that had a status change since INotifications.last.

        """

    def notify(urls):
        """Send notifications about given urls."""


class IThreadPool(zope.interface.Interface):
    """Thread pool for the checker."""

    limit = zope.schema.Int(
        title=u'Maximum number of concurrent active threads')

    active = zope.interface.Attribute(u'Set of active threads')

    available = zope.schema.Int(
        title=u'Number of currently available threads',
        readonly=True)


class ICheckerThread(zope.interface.Interface):

    url = zope.schema.URI(
        title=u'URL')

    state = zope.schema.Choice(
        title=u'State',
        source=StateSource(),
        required=False)

    reason = zope.schema.TextLine(
        title=u'Reason for state',
        required=False)


class ISchemeHandler(zope.interface.Interface):
    """Provides protocol-specific handling of a URL for one scheme."""

    def allow(url):
        """Determine whether to allow a URL to be registered or checked."""

    def check(url):
        """Check a URL and return a status tuple: (status, reason)"""

    def classify(url):
        """Determine the URL class."""


class ISynchronization(zope.interface.Interface):
    """Synchronize a client's database with the LMS's."""

    last = zope.schema.Datetime(
        title=u'Last notified')

    force = zope.schema.Bool(
        title=u'Force a synchronisation')

    def sync():
        """Perform the synchronization."""


class IStatistics(zope.interface.Interface):
    """Statistical information for munin."""

    thread_pool = zope.interface.Attribute('Number of threads currently used.')

    queue_size = zope.interface.Attribute('Number of items currently in the queue.')
