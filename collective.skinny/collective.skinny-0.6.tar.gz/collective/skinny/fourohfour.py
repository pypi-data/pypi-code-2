from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from collective.skinny.base import BaseView
import collective.skinny.interfaces

class View(BaseView):
    """This view will return a 404 instead of the usual
    ``standard_error_message`` when we're in the public skin.
    """
    template = ViewPageTemplateFile('templates/404.pt')

    def __call__(self):
        if collective.skinny.interfaces.IPublicLayer.providedBy(self.request):
            # If we're in the public skin, we return a 404:
            self.request.response._locked_status = 0
            self.request.response.setStatus(404)
            return self.template()
        else:
            # If not, we'll fall back to the standard error message:
            skins = getToolByName(self.context, 'portal_skins')
            return skins.plone_templates.standard_error_message.__of__(
                self.context)()
