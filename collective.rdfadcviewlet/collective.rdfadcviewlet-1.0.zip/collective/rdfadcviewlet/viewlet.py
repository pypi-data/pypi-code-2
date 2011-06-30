from Acquisition import aq_inner

from plone.app.layout.viewlets.common import DublinCoreViewlet, ViewletBase
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class RDFaDublinCoreViewlet(ViewletBase):

    index = ViewPageTemplateFile('dublin_core.pt')

    def update(self):
        plone_utils = getToolByName(self.context, 'plone_utils')
        context = aq_inner(self.context)
        metatags = plone_utils.listMetaTags(context)
        rdfa = {}
        for key, value in metatags.items():
            rdfa[key.replace('DC.', 'dc:')] = value

        self.metatags = rdfa.items()
