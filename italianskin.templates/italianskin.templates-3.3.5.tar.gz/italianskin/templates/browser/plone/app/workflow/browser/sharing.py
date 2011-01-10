from plone.app.workflow.browser.sharing import SharingView as CustomSharingView

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class SharingView(CustomSharingView):
    # Actions
    
    template = ViewPageTemplateFile('sharing.pt')
    
