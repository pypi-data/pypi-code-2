from zope.component import getMultiAdapter

from Products.Five import BrowserView as FiveView

from Products.CMFCore.utils import getToolByName as _t

from plone.app.viewletmanager.manager import OrderedViewletManager

from collective.projekktor.interfaces import IProjekktorProvider

class ProjekktorViewletManager( OrderedViewletManager ):
    def __init__(self,context,request,container,*la,**kwa):
        super(ProjekktorViewletManager,self).__init__(context,request,container,*la,**kwa)

class ProjekktorPlayerViewlet( FiveView ):
    def __init__( self, context, request, view, manager):
        super(ProjekktorPlayerViewlet,self).__init__(context, request)
        self.provider = getMultiAdapter((context,view),IProjekktorProvider)
        
    def getFilepath(self):
        return self.provider.getFilepath()

    def getAlternativeFilepaths(self):
        return self.provider.getAlternativeFilepaths()

    def getPoster(self):
        return self.provider.getPoster()

    def getWidth(self):
        return self.provider.getWidth()

    def getHeight(self):
        return self.provider.getHeight()        

    def getMimetype(self):
        return self.provider.getMimetype()

    def getTitle( self ):
        return self.provider.getTitle()

    def getDescription( self ):
        return self.provider.getDescription()

    def isVideo(self):
        return self.provider.isVideo()

    def isAudio(self):
        return self.provider.isAudio()
