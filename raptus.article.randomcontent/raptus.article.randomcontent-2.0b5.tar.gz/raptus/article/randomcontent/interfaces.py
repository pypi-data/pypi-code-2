from zope import interface

class IRandomContent(interface.Interface):
    """ Provider for a random article
    """
    
    def getArticle(**kwargs):
        """ Returns a random article (catalog brain)
        """