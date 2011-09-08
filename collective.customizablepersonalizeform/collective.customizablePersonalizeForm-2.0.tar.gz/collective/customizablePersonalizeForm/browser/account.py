from zope.interface import implements

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView

from plone.app.users.browser.interfaces import IAccountPanelForm, IAccountPanelView

from plone.app.users.browser.account import AccountPanelView

class ExtendedAccountPanelView(AccountPanelView):
    template = ViewPageTemplateFile('templates/extended-account-panel-bare.pt')


