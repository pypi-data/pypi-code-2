from Acquisition import aq_inner, aq_parent
#from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.CMFPlone.utils import safe_unicode
from Products.statusmessages.interfaces import IStatusMessage

class Miscellaneous(BrowserView):

    def verkkomaksut_canceled(self):
        context = aq_inner(self.context)
        message = safe_unicode(context.getCancel_message())
        IStatusMessage(self.request).addStatusMessage(message, type='info')
        url = aq_parent(context).absolute_url()
        self.request.response.redirect(url)

    def verkkomaksut_notify(self):
        pass
