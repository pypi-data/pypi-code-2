from zope import component
from zope.interface import implements
from random import *

from plone.app.layout.viewlets.common import ViewletBase

from Products.ATContentTypes.interface.image import IATImage
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot

from raptus.header import headerMessageFactory as _
from raptus.header.interfaces import IHeader

from Acquisition import aq_inner, aq_parent

class HeaderViewlet(ViewletBase):
    index = ViewPageTemplateFile('header.pt')
    
    hasImage = False
    src = ''
    description = ''
    title = ''
    manage = None
    
    def update(self):
        self.hasImage = False
        catalog = getToolByName(self.context, 'portal_catalog')
        props = getToolByName(self.context, 'portal_properties').site_properties

        parent = aq_inner(self.context)
        while True:
            brain = catalog(object_provides=IHeader.__identifier__,
                            path={'query': '/'.join(parent.getPhysicalPath()),'depth': 1})
            if len(brain) or IPloneSiteRoot.providedBy(parent) or not props.getProperty('header_allow_inheritance', True):
                break
            else:
                parent = aq_parent(parent)
        if not len(brain):
            return
        
        """take the first header-element
        """
        header = brain[0]
        images = catalog(object_provides=IATImage.__identifier__,
                            path={'query': header.getPath(),'depth': 1})

        if not len(images):
            return

        image = choice(images)
        obj = image.getObject()
        scales = component.getMultiAdapter((obj, obj.REQUEST), name='images')
        scale = scales.scale('image',
                             width=(props.getProperty('header_width', 1000000)),
                             height=(props.getProperty('header_height', 1000000)))
        if scale is None:
            return

        self.image = scale.tag()
        self.description = image['Description']
        self.title = image['Title']
        """ if article core exist, so this will load the manage box
        """

        self.hasImage = True

        try:
            from raptus.article.core import interfaces
            manageable = interfaces.IManageable(self.context)
            self.manage = manageable.getList([image]).pop()
        except ImportError:
            pass

    def render(self):
        if self.hasImage:
            return self.index()
        else:
            return ''