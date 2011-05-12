from Products.Archetypes.interfaces.storage import IStorage


class IExternalStorage(IStorage):
    """ Marker for distinguishing ExternalStorage """

    def publicizeInstance(self, instance):
        """ copy private version to public version """

    def revertInstance(self, instance):
        """ copy public version back to private version """

    # here is to discuss what such things mean to folder like types ;)
