"""
ZCML registrations.
"""
from zope import interface
from zope.component import getUtility
from zope.configuration.fields import Path
from collective.amberjack.core.interfaces import ITourRegistration

import os

class ITourDirective(interface.Interface):
    """Create tour registration."""

    tourlocation = Path(
        title=u'Location where you placed the tour',
        description=u'The variable that points to the tour',
        required=True)

def _zipregisterTour(source, filename):
    reg = getUtility(ITourRegistration, 'zipfile')
    registration = reg(source, filename=filename)
    registration.register()

def _folderregisterTour(path):
    reg = getUtility(ITourRegistration, 'folder')
    registration = reg(None, filename=path)
    registration.register()

def tour(_context, tourlocation):
    """Tour class factory registration."""
    if os.path.isdir(tourlocation): #perform dir registration
        _context.action(
            discriminator = '_registerTour:%s' % tourlocation,
            callable = _folderregisterTour,
            args = (tourlocation, )
        )
    else:
        archive = open(tourlocation,'r')
        archive.seek(0)
        source = archive.read()
        archive.close()
        filename = os.path.basename(tourlocation)
        _context.action(
            discriminator = '_registerTour:%s' % tourlocation,
            callable = _zipregisterTour,
            args = (source, filename)
        )

