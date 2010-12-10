from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage


class SaveDraftView(BrowserView):
    
    def __call__(self):
        # save the request values to the draft storage
        uid = self.request.form['fg_uid']
        drafts = getToolByName(self.context, 'portal_fg_drafts')
        drafts.saveDraft(uid, self.request)

        catalog = getToolByName(self.context, 'portal_catalog')
        form = catalog.unrestrictedSearchResults(UID=uid)[0].getObject()
        if 'draft-stored' in form.objectIds():
            # if there's a custom "draft stored" message, redirect to it
            self.request.response.redirect(form.absolute_url + '/draft-stored')
        else:
            # otherwise show a simple status message on the form
            IStatusMessage(self.request).addStatusMessage('Draft saved.')
            self.request.response.redirect(form.absolute_url())