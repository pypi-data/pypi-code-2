from zope.component import adapts, getUtility
from zope.interface import implements
from collective.projekktor.interfaces import IProjekktorMedia, IProjekktorUtility
from Products.ATContentTypes.interfaces.file import IATFile
from Products.ATContentTypes.interfaces.image import IATImage


class ProjekktorMedia(object):
    adapts(IATFile)
    implements(IProjekktorMedia)

    def __init__(self,context):
        self.context = context

    @property
    def projekktor(self):        
        return getUtility(IProjekktorUtility)        

    @property
    def _audio_mimetypes(self):
        return self.projekktor.audio_mimetypes

    @property
    def _video_mimetypes(self):
        return self.projekktor.video_mimetypes

    def _getSiblings(self,iface=None):
        fileid = self.context.getId()
        parts = fileid.split(".")
        if len(parts)>1:
            parts.pop()
        fileroot = '.'.join(parts)
        siblings = [y for x,y in self.context.contentItems() 
                    if (x.startswith('%s.'%fileroot) or x==fileroot)
                    and not x==fileid]
        if iface:
            return [y for y in siblings if iface.providedBy(y)]
        return siblings

        
    def isVideo(self):
        if self.getMimetype() in self._video_mimetypes:
            return True
        return False

    def isAudio(self):
        if self.getMimetype() in self._audio_mimetypes:
            return True
        return False

    def getFilepath(self):
        return self.context.absolute_url()

    def getAlternativeFilepaths(self):
        siblings = self._getSiblings(IATFile)
        mimes = self.isVideo() and self._video_mimetypes or self._audio_mimetypes
        filepaths = {}
        [filepaths.__setitem__(x.absolute_url().split('/')[-1],x.absolute_url()) 
         for x in siblings if x.getContentType() in mimes]
        return filepaths

    def getMimetype(self):
        return self.context.getContentType()

    def getTitle(self):
        return self.context.Title()

    def getDescription(self):
        return self.context.Description()

    def getPoster(self):
        siblings = self._getSiblings(IATImage)
        if siblings:
            return siblings[0].absolute_url()
        return self.isVideo() and self.projekktor.video_poster or self.projekktor.audio_poster

    def getWidth(self):
        return self.projekktor.video_width
    def getHeight(self):
        return self.projekktor.video_height
    
