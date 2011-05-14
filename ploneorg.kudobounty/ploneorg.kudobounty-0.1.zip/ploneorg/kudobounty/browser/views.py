import time
from DateTime import DateTime
from Acquisition import aq_parent
from zope.interface import implements, Interface
from zope.component import getUtility, queryUtility
from zope.component import getMultiAdapter
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from plone.i18n.normalizer.interfaces import IURLNormalizer
from plone.registry.interfaces import IRegistry

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.config import RENAME_AFTER_CREATION_ATTEMPTS

from ploneorg.kudobounty import logger
from ploneorg.kudobounty.config import *
from ploneorg.kudobounty import kudobountyMessageFactory as _
from ploneorg.kudobounty.content.bountyprogramsubmission import calcTitle

from collective.portlet.collectionmultiview.renderers.base import (
                                    CollectionMultiViewBaseRenderer)

class BountyCollectionRenderer(CollectionMultiViewBaseRenderer):
    __name__ = 'Bounty Collection View'
    template = ViewPageTemplateFile('bounty_collection_view.pt')


class BountyFormProcessorView(BrowserView):
    """
    Browser page view for automation of 'Bounty Program Submission'
    content object creation.
    """

    @property
    def portal(self):
        return getMultiAdapter((self.context, self.request),
                               name='plone_portal_state').portal()

    @property
    def wftool(self):
        return getMultiAdapter((self.context, self.request),
                               name='plone_tools').workflow()

    def __call__(self):
        """
        Perform following steps:
          * Get container for submissions;
          * Create bounty submission object in the container
            and fill it in with data, submitted with the PFG form;
          * Set effective and expiration date to nearest month;
          * Change the workflow state into pending state.
        """
        # Get submissions container - assumed, that 
        # PFG form located in the same container.
        container = aq_parent(self.context)
        # Create Bounty Program Submission object
        form = self.request.form
        title = calcTitle(form['firstName'], form['lastName'], form['organization'])
        id = self.getUniqueId(container, title)
        container.invokeFactory("Bounty Program Submission", id)
        bps = getattr(container, id)
        # Update Submission with data from the PFG form
        form['image'] = form['image_file']
        form['description'] = form['altText']
        effd, expd = self.getEffExpDates()
        form['effectiveDate'] = effd
        form['expirationDate'] = expd

        bps.update(**form)
        bps.unmarkCreationFlag()
        bps.reindexObject()
        # Change wf state
        self.wftool.doActionFor(bps, "submit")

        return {}

    def getEffExpDates(self):
        now = DateTime()
        month = now.month()
        year = now.year()
        if month == 12:
            month = 1
            year = year + 1
        else:
            month = month + 1
        effd = DateTime(year, month, 1, 0, 0)
        expd = DateTime(year, month + 1, 1, 23, 55) - 1
        return effd, expd
        

    def getUniqueId(self, container, title):
        # NOTE:
        # Mixed and little refactored functions of
        # Products.Archetypes.BaseObject.BaseObject class:
        #  * _findUniqueId (check uniqueness of id in the container)
        #  * generateNewId (used url noralizer utility)
        id = queryUtility(IURLNormalizer).normalize(title)
        if not id:
            id = str(time.time())
        container_ids = container.objectIds()
        check_id = lambda id, required: id in container_ids

        invalid_id = check_id(id, required=1)
        if not invalid_id:
            return id

        idx = 1
        while idx <= RENAME_AFTER_CREATION_ATTEMPTS:
            new_id = "%s-%d" % (id, idx)
            if not check_id(new_id, required=1):
                return new_id
            idx += 1

        return None

class BountySubmissionView(BrowserView):
    """
    Browser page view for 'Bounty Program Submission' view.
    """

    def data(self):
        field_names = ['remoteUrl', 'description', 'mission', 'image']
        schema = self.context.Schema()
        res = []
        for fn in field_names:
            field = schema.getField(fn)
            ftype = field.getType().split('.')[-1]
            if ftype == 'ImageField':
                value = field.tag(self.context, scale="bounty",
                                  alt=self.context.Description())
            else:
                value = field.getAccessor(self.context)()

            res.append({"fieldName": fn, 
                        "label": field.widget.Label(self.context),
                        "fieldType": ftype,
                        "value": value})
        return res

            
