from zope import interface

class IRandomImage(interface.Interface):
    """ Provider for a random image
    """
    
    def getImage(**kwargs):
        """ Returns a random image (catalog brain)
        """