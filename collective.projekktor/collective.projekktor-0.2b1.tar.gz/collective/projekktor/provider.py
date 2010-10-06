from collective.projekktor.interfaces import IProjekktorMedia

class ProjekktorProvider(object):
    
    def __init__(self,context,request):
        self.context = context

    @property
    def target(self):
        return self.context
    
    @property
    def projekktor(self):
        return IProjekktorMedia(self.target)
        
    def getFilepath(self):
        if not isinstance(self.target,str):
            return self.projekktor.getFilepath()
        return self.target

    def getMimetype(self):
        if not isinstance(self.target,str):
            return self.projekktor.getMimetype()
        return ''

    def getTitle( self ):
        if not isinstance(self.target,str):
            return self.projekktor.getTitle()
        return self.target.split('/').pop()

    def getDescription( self ):
        if not isinstance(self.target,str):
            return self.projekktor.getDescription()
        return ''

    def isVideo(self):
        if not isinstance(self.target,str):
            return self.projekktor.isVideo()
        return False        

    def isAudio(self):
        if not isinstance(self.target,str):
            return self.projekktor.isAudio()
        return False        

    def isVideo(self):
        return self.projekktor.isVideo()

    def isAudio(self):
        return self.projekktor.isAudio()

    def getFilepath(self):
        return self.projekktor.getFilepath()

    def getAlternativeFilepaths(self):
        return self.projekktor.getAlternativeFilepaths()

    def getMimetype(self):
        return self.projekktor.getMimetype()

    def getTitle(self):
        return self.projekktor.getTitle()

    def getDescription(self):
        return self.projekktor.getDescription()

    def getPoster(self):
        return self.projekktor.getPoster()

    def getWidth(self):
        return self.projekktor.getWidth()

    def getHeight(self):
        return self.projekktor.getHeight()
