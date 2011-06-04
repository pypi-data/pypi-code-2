from Acquisition import aq_inner
from DateTime import DateTime

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException

from plone.app.layout.viewlets.content import DocumentBylineViewlet as base
from plone.memoize.instance import memoize


class DocumentBylineViewlet(base):

    index = ViewPageTemplateFile("document_byline.pt")

    @memoize
    def pub_date(self):
        """Return object published date if it's currently in published
        workflow state.
        """
        context = aq_inner(self.context)
        workflow = getToolByName(context, 'portal_workflow')
        review_history = []
        try:
            review_history = workflow.getInfoFor(context, 'review_history')
        except WorkflowException:
            return None
        
        if len(review_history) > 0:
           info = review_history[-1]
           if info['review_state'] == 'published':
               return info['time']

        return None
    
    def mod_date(self):
        """Return modification date if object was modified after it was
        published, or if object is not published yet.
        """
        modified = DateTime(self.context.ModificationDate())
        published = self.pub_date()
        if modified is not None and published is not None and \
           modified <= published:
            return None
        
        return modified
