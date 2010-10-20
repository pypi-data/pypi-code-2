from zope.interface import Interface

class IContentFlowBrainProvider(Interface):
    """ Provides the items as brains to display for a given context
    """
    
    def __call__():
        """ Returns a list of catalog brains
        """
        
class IContentFlowProvider(Interface):
    """ Provides the items to display for a given context
    """
    
    def __call__():
        """ Returns a list of dicts with the following keys:
        
            img: the url to the image to be displayed
            title: the caption to be displayed
            url: a link to be placed on the image
        """

class IContentFlowProperties(Interface):
    """ Provides the properties for a given context
    """
    
    def __call__():
        """ Return a list of key, value tuples
        """

class IContentFlow(Interface):
    """ Marker interface for views or objects on which to display ContentFlow
        viewlet
    """
