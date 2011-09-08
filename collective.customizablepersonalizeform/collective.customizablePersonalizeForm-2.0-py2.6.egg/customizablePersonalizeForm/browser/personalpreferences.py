from plone.app.users.browser.personalpreferences import UserDataPanel

from OFS.Image import Image

from collective.customizablePersonalizeForm.adapters.interfaces import IExtendedUserDataWidgets

from zope.component import getAdapters

class ExtendedUserDataPanel(UserDataPanel):

    def isImage(self, widget):
        return isinstance(widget._data, Image)

    def __init__(self, context, request):
        """ Load the UserDataSchema at view time.

        (Because doing getUtility for IUserDataSchemaProvider fails at startup
        time.)

        """
        super(ExtendedUserDataPanel, self).__init__(context, request)
        providers = [x for x in getAdapters( (context, request,) , IExtendedUserDataWidgets)]
        for provider in providers:
            for association in provider[1].getWidgets():
                self.form_fields[association['field']].custom_widget = association['factory']
