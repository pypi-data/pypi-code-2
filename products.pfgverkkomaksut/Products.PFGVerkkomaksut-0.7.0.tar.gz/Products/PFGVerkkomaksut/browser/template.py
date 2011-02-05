from Acquisition import aq_inner#, aq_parent
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
#from Products.statusmessages.interfaces import IStatusMessage
#from Products.PFGVerkkomaksut import PFGVerkkomaksutMessageFactory as _

class PFGVerkkomaksutSuccessView(BrowserView):

    template = ViewPageTemplateFile('templates/verkkomaksut_success.pt')

    def __call__(self):
        return self.template()

    def message(self):
        context = aq_inner(self.context)
        sdm = getToolByName(context, 'session_data_manager')
        session = sdm.getSessionData(create=False)
        if session and session.has_key('pfg.verkkomaksut'):
            pfgv = session.get('pfg.verkkomaksut', None)
            if pfgv is not None:
                uid = pfgv.get('ADAPTER_UID', None)
                if uid is not None:
                    reference_catalog = getToolByName(context, 'reference_catalog')
                    adapter = reference_catalog.lookupObject(uid)
                    return adapter.getThanksPrologue()
