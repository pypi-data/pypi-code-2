from zope import interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from browser.interfaces import *

class IPublicSkinLayer(IDefaultBrowserLayer):
    """ Layer for the public view """

class IRuleOverwrite(interface.Interface):
    """ Interface to make rule overwrite possible """

    def mustDisplayPublicView(context, request):
        pass
