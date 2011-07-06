"""
minimal zope3 style store
"""

from zope import interface
from zope.app.component import site

import interfaces

class Store( site.SiteManagerContainer ):

    interface.implements( interfaces.IStore )
