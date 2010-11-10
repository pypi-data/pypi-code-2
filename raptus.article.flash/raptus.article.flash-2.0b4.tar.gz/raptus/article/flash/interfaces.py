from zope import interface

class IFlashs(interface.Interface):
    """ Provider for flash movies contained in an article
    """
    
    def getFlashs(**kwargs):
        """ Returns a list of flash movies (catalog brains)
        """

class IFlashSize(interface.Interface):
    """ Handler for sizing of flash files
    """
        
    def getSize(size="original"):
        """
        Returns the width and height registered for the specific size
        
        The sizes are taken from the raptus_article properties sheet
        and are formed by the following name schema:
        
            flash_<size>_(height|width)
        """

class IFlash(interface.Interface):
    """ Marker interface for the flash content type
    """
