from zope.interface import Interface


class IMemberProfileInstalledLayer(Interface):
    """A layer specific for this add-on product.

    This interface is referred in browserlayers.xml.

    All views and viewlets register against this layer will appear on your Plone site
    only when the add-on installer has been run.
    """


class IProfileUtils(Interface):
    """ Utility to handle member profile creation.
    """
    def create(context):
        """ Create member area for loged in user
        """

    def set_name(fullname, userfolder):
        """ Set the name of a user on userfolder """

class IMemberProfileSettingsAdapter(Interface):
    """ Handles persistent settings for member profiles.
        Stores values in a persistent dict.
    """
    
    def get(key):
        """ Return value of key. Return None if it doesn't exist.
        """
        
    def set(key, value):
        """ Set key to value.
        """
        
class IProfileComplete(Interface):
    """
    """
    
    def is_complete():
        """ """
