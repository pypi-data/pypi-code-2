from zope import interface, component

from plone.memoize.instance import memoize
from plone.app.layout.viewlets.common import ViewletBase

from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core import interfaces

class IBacklink(interface.Interface):
    """ Marker interface for the backlink viewlet
    """

class Component(object):
    """ Component which shows a back link using raptus.backlink
    """
    interface.implements(interfaces.IComponent)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Back link')
    description = _(u'A link back to the next higher level.')
    image = '++resource++backlink.gif'
    interface = IBacklink
    viewlet = 'raptus.article.backlink'
    
    def __init__(self, context):
        self.context = context

class BacklinkViewlet(ViewletBase):
    """ Overrides the default backlink viewlet for articles
    """
    def index(self):
        return ''
