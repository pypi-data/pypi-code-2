from plone.app.contentmenu.view import ContentMenuProvider as ContentMenuProviderOriginal
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

class ContentMenuProvider(ContentMenuProviderOriginal):
    """Content menu provider for the "view" tab: displays the menu
    """
    render = ZopeTwoPageTemplateFile('contentmenu.pt')
