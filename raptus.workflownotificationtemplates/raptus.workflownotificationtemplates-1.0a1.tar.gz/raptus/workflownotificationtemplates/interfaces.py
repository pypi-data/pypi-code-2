from zope.interface import Interface

class IPossibleNotificationTemplates(Interface):
    """Utility to provide a list of (value, title) pairs of possible
       names of notification templates to be added through the configlet
    """
    
    def names(context):
        """
        """
