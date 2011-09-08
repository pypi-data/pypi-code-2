from zope.interface import Interface, implements
from zope.component import getAdapters

from plone.app.users.userdataschema import IUserDataSchemaProvider, IUserDataSchema

from collective.customizablePersonalizeForm.adapters.interfaces import IExtendedUserDataSchema

from zope.site.hooks import getSite

class ExtendedUserDataSchemaProvider(object):
    implements(IUserDataSchemaProvider)

    def getSchema(self):
        """ Returns the extended schema interfaces with adapter provided fields
        """
        site = getSite()
        providers = [x for x in getAdapters( (site, site.REQUEST,) , IExtendedUserDataSchema)]

        for provider in providers:
            bases  = [x for x in IExtendedUserDataSchema.getBases()]
            new = provider[1].getSchema()
            if new._InterfaceClass__attrs != {}:
                #Make the IExtendedUserDataSchema inherits from the new interface
                if new not in bases:
                    bases.append(new)
                IExtendedUserDataSchema._Specification__setBases(tuple(bases))
                #Copy the fields from the interface to IExtendedUserDataSchema
                for x in new._InterfaceClass__attrs.keys():
                    if x not in IExtendedUserDataSchema._InterfaceClass__attrs.keys():
                        IExtendedUserDataSchema._InterfaceClass__attrs[x] = new._InterfaceClass__attrs[x]
                        IExtendedUserDataSchema._InterfaceClass__attrs[x].interface = IExtendedUserDataSchema
        return IExtendedUserDataSchema
