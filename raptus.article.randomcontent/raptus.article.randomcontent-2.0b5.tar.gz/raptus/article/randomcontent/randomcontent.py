import random

from zope import interface, component

from raptus.article.core.interfaces import IArticle
from raptus.article.nesting.interfaces import IArticles
from raptus.article.randomcontent.interfaces import IRandomContent

class RandomContent(object):
    """ Provider for a random article
    """
    interface.implements(IRandomContent)
    component.adapts(IArticle)
    
    def __init__(self, context):
        self.context = context
        
    def getArticle(self, **kwargs):
        """ Returns a random article (catalog brain)
        """
        provider = IArticles(self.context)
        articles = provider.getArticles(**kwargs)
        if not len(articles):
            return None
        return articles[random.randint(0, len(articles)-1)]
