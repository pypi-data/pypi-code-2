#author: marc goetz

from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from realmstatus_api import Realmstatus
from collective.wowcharacter.interfaces import IWoWCharacter

class IRealmstatusPortlet(IPortletDataProvider):
    """ A portlet """ 

class Assignment(base.Assignment):
    """ Portlet assignment """ 

    implements(IRealmstatusPortlet)

    def __init__(self):
        pass

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen."""

        return "WoWRealmstatus"

class Renderer(base.Renderer):
    """ Portlet renderer """

    render = ViewPageTemplateFile("wowrealmstatus.pt")

    # make sure the portlet is only showed for a wowcharacter
    def visible(self):

        return IWoWCharacter.providedBy(self.context)

    # get realmstatus
    def realm_status(self):

        self.realmstatus = Realmstatus()

        self.realm = self.context.realm

        return self.realmstatus.get_realm_status(self.realm) == "Realm Up"

    #get realmtype
    def realm_type(self):

        return self.realmstatus.get_realm_type(self.realm)

class AddForm(base.AddForm):
    """ Portlet add form """

    form_fields = form.Fields(IRealmstatusPortlet)

    def create(self, data):
        return Assignment(**data)
