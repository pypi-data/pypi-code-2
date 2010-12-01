from random import choice
from Acquisition import aq_inner, aq_parent

from zope.component import getMultiAdapter

from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

from Products.ATContentTypes.interface.image import IATImage
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot

from raptus.header.interfaces import IHeader

class HeaderFaderViewlet(ViewletBase):
    index = ViewPageTemplateFile('headerfader.pt')

    @property
    @memoize
    def images(self):
        images = []
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
        header = brain[0]
        brains = catalog(object_provides=IATImage.__identifier__,
                         path={'query': header.getPath(),'depth': 1})
        if not len(brains):
            return
        random = choice(brains)
        for brain in brains:
            obj = brain.getObject()
            scales = getMultiAdapter((obj, self.request), name='images')
            scale = scales.scale('image',
                                 width=(props.getProperty('header_width', 1000000)),
                                 height=(props.getProperty('header_height', 1000000)))
            if scale is None:
                continue
            images.append({'image': scale.url,
                           'title': brain.Title,
                           'description': brain.Description,
                           'current': brain is random})
        images.sort(cmp=lambda x,y: (x['current'] and -1 or 0))
        return images
