from plone.app.contentrules.browser.controlpanel import ContentRulesControlPanel as CustomContentRulesControlPanel

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class ContentRulesControlPanel(CustomContentRulesControlPanel):

    template = ViewPageTemplateFile('templates/controlpanel.pt')