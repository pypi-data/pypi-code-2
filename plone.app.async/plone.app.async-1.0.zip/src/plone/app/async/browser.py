import logging
import transaction

from zope.component import getUtility
from AccessControl import getSecurityManager
from Products.Five import BrowserView
from plone.app.async.interfaces import IAsyncService

logger = logging.getLogger('ASYNCTEST')


def aJob(context):
    user = getSecurityManager().getUser()
    logger.info('%r %r %r %r' % (
        context,
        context.portal_url.getPortalObject(),
        getattr(user, 'aq_parent', None),
        user))


class AsyncTestView(BrowserView):

    def __call__(self):
        async = getUtility(IAsyncService)
        async.queueJob(aJob, self.context)
        transaction.commit()
