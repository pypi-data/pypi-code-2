from zope.i18n import translate

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _p

from raptus.browsermessage.config import BROWSERS

class BrowserMessageConfiglet(BrowserView):
    template = ViewPageTemplateFile("configlet.pt")
    
    def __call__(self, browsers=None, suggest=None):
        properties = getToolByName(self.context, 'portal_properties').browsermessage_properties
        actions = getToolByName(self.context, 'portal_actions')['browsermessage_actions']
        if browsers is not None or suggest is not None:
            properties._updateProperty('browsers', browsers)
            
            for id in actions.keys():
                action = actions[id]
                action._updateProperty('visible', id in suggest)
            
            statusmessage = IStatusMessage(self.request)
            statusmessage.addStatusMessage(translate(_p("Changes saved."), context=self.request), 'info')
        
        self.suggest = [{'id': action.id,
                         'title': action.title,
                         'visible': action.visible} for action in actions.listActions()]
        
        self.browsers = []
        browsers = properties.getProperty('browsers', [])
        for browser, title in BROWSERS:
            item = {'id': browser,
                    'title': title,
                    'checked': browser in browsers}
            self.browsers.append(item)
        return self.template()
        