from zope.interface import implements
from Products.Five import BrowserView as FiveView

from collective.projekktor.interfaces import IProjekktorMedia, IProjekktorProvider
from collective.projekktor.provider import ProjekktorProvider

class ProjekktorViewProvider(ProjekktorProvider):            
    implements(IProjekktorProvider)


class ProjekktorView (FiveView):
    """Projekktor View for Plone filetypes"""

    def __init__(self,context,request):
        super(ProjekktorView,self).__init__(context,request)
        self.media = IProjekktorMedia(self.context)

    def getTitle(self):
        return self.media.getTitle()

    def getDescription(self):
        return self.media.getDescription()
