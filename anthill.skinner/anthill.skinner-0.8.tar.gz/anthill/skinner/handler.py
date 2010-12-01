
from zope.interface import implements
from zope.component import getMultiAdapter

from plone.memoize.forever import memoize
from Products.CMFCore.utils import getToolByName

from interfaces import IRuleOverwrite 

import logging
log = logging.getLogger('anthill.skinner')

@memoize
def installed(context):
    qi = getToolByName(context, 'portal_quickinstaller')
    if qi:
        if qi.isProductInstalled('anthill.skinner'):
            return True

    return False

def beforeTraverseHandler(context, event):
    """ This handler is the main working horse and checks if
        public skin should be enabled. That means marking the
        request with IPublicSkinLayer. """

    try:
        if not installed(context):
            log.debug('disabled for %s' % str(context))
            return
    except Exception, ex:
        # can fail because of memoize or context type problems
        # in this case we always return plone view but with
        # meaningful error message in logs
        log.error('Could not check for skinner on context %s (%s) - falling back to plone skin!' % (str(context), str(ex)))
        return

    skinner = getMultiAdapter( (context, event.request), name=u'skinner')
    if skinner.mustDisplayPublicView() is True:
        skinner.activatePublicSkin()
