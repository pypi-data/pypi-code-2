from Products.CMFCore.utils import getToolByName

from AccessControl import ClassSecurityInfo

from collective.customizablePersonalizeForm.adapters.interfaces import IExtendedUserDataPanel #, IExampleUserDataSchema

from plone.app.users.browser.personalpreferences import UserDataPanelAdapter
from plone.app.users.browser.account import AccountPanelSchemaAdapter

from zope.site.hooks import getSite
from zope.component import getAdapters

from Acquisition import aq_inner

class EnhancedUserDataPanelAdapter(UserDataPanelAdapter):

    real_context = None

    def __init__(self, context):
        self.real_context = context
        providers = [x for x in getAdapters( (context, context.REQUEST,) , IExtendedUserDataPanel)]
        for provider in providers:
            for prop in provider[1].getProperties():
                if isinstance(prop, dict):
                    setattr(self.__class__, prop['name'], property(prop['getter'], prop['setter']))
                else:
                    setattr(self.__class__, prop, self.make_prop(prop))
        # INITIALIZES THE CURRENT SELF.CONTEXT AS A USER ID, LIKE self.context = 'admin'
        super(EnhancedUserDataPanelAdapter, self).__init__(context)

    def make_prop(self, name ):
        def getter(self):
            return self.context.getProperty(name, '')
        def setter(self, value):
            return self.context.setMemberProperties({name : value})
        return property(getter, setter)

