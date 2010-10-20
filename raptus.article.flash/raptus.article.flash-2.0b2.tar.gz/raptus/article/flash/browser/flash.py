from Acquisition import aq_inner
from zope import interface, component

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core import interfaces
from raptus.article.flash.interfaces import IFlashs, IFlashSize

class IFlashLeft(interface.Interface):
    """ Marker interface for the flash left viewlet
    """

class ComponentLeft(object):
    """ Component which lists the maps on the left side
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Flash left')
    description = _(u'List of flash files contained in the article on the left side.')
    image = '++resource++flash_left.gif'
    interface = IFlashLeft
    viewlet = 'raptus.article.flash.left'
    
    def __init__(self, context):
        self.context = context

class ViewletLeft(ViewletBase):
    """ Viewlet listing the flash files on the left side
    """
    index = ViewPageTemplateFile('flash.pt')
    css_class = "componentLeft flash-left"
    component = "flash.left"
    size = "left"
    
    def _class(self, brain, i, l):
        cls = []
        if i == 0:
            cls.append('first')
        if i == l-1:
            cls.append('last')
        if i % 2 == 0:
            cls.append('odd')
        if i % 2 == 1:
            cls.append('even')
        return ' '.join(cls)
    
    @memoize
    def movies(self):
        provider = IFlashs(self.context)
        manageable = interfaces.IManageable(self.context)
        items = manageable.getList(provider.getFlashs(component=self.component), self.component)
        i = 0
        l = len(items)
        for item in items:
            w, h = IFlashSize(item['obj']).getSize(self.size)
            item.update({'uid': item['brain'].UID,
                         'title': item['brain'].Title,
                         'description': item['brain'].Description,
                         'url': item['brain'].getURL(),
                         'class': self._class(item['brain'], i, l),
                         'width': w,
                         'height': h})
            i += 1
        return items

class IFlashRight(interface.Interface):
    """ Marker interface for the flash right viewlet
    """

class ComponentRight(object):
    """ Component which lists the flash files on the right side
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Flash right')
    description = _(u'List of flash files contained in the article on the right side.')
    image = '++resource++flash_right.gif'
    interface = IFlashRight
    viewlet = 'raptus.article.flash.right'
    
    def __init__(self, context):
        self.context = context

class ViewletRight(ViewletLeft):
    """ Viewlet listing the flash files on the right side
    """
    css_class = "componentRight flash-right"
    component = "flash.right"
    size = "right"

class IFlashFull(interface.Interface):
    """ Marker interface for the flash full viewlet
    """

class ComponentFull(object):
    """ Component which lists the flash files over the whole width
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Flash')
    description = _(u'List of flash files contained in the article over the whole width.')
    image = '++resource++flash_full.gif'
    interface = IFlashFull
    viewlet = 'raptus.article.flash.full'
    
    def __init__(self, context):
        self.context = context

class ViewletFull(ViewletLeft):
    """ Viewlet listing the flash files over the whole width
    """
    css_class = "componentFull flash-full"
    component = "flash.full"
    size = "full"

class IFlashTeaser(interface.Interface):
    """ Marker interface for the flash teaser viewlet
    """

class ComponentTeaser(object):
    """ Component which lists the flash files over the whole width above the columns
    """
    interface.implements(interfaces.IComponent, interfaces.IComponentSelection)
    component.adapts(interfaces.IArticle)
    
    title = _(u'Flash teaser')
    description = _(u'List of flash files contained in the article over the whole width and displayed above the columns.')
    image = '++resource++flash_teaser.gif'
    interface = IFlashTeaser
    viewlet = 'raptus.article.flash.teaser'
    
    def __init__(self, context):
        self.context = context

class ViewletTeaser(ViewletLeft):
    """ Viewlet listing the flash files over the whole width above the columns
    """
    css_class = "componentFull flash-full"
    component = "flash.teaser"
    size = "teaser"
    
