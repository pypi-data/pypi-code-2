from zope.interface import Interface as I
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from collective.projekktor import projekktorMessageFactory as _

class IProjekktorVideoConfig(I):
    """This interface defines the config properties."""

    video_mimetypes = schema.List(
        title=_(u"Video mimetypes")
        ,description=_(u"List video mimetypes here")
        ,required=False
        ,value_type=schema.TextLine()
        ,default=[]) 

    video_poster = schema.TextLine(
        title=_(u"Video poster"),
        description=_(u"Default video poster"),
        required=False) 

    video_width = schema.TextLine(
        title=_(u"Video width")
        ,description=_(u"Default video width")
        ,required=False) 

    video_height = schema.TextLine(
        title=_(u"Video height"),
        description=_(u"Default video height"),
        required=False) 


class IProjekktorAudioConfig(I):
    """This interface defines the config properties."""

    audio_mimetypes = schema.List(
        title=_(u"Audio mimetypes")
        ,description=_(u"List audio mimetypes here")
        ,required=False
        ,value_type=schema.TextLine()
        ,default=[]) 

    audio_poster = schema.TextLine(
        title=_(u"Audio poster"),
        description=_(u"Default audio poster"),
        required=False) 

    audio_width = schema.TextLine(
        title=_(u"Audio width")
        ,description=_(u"Default audio width")
        ,required=False) 

    audio_height = schema.TextLine(
        title=_(u"Audio height"),
        description=_(u"Default audio height"),
        required=False) 
    

class IProjekktorUtility(
    IProjekktorVideoConfig,
    IProjekktorAudioConfig,
    ):
    """This interface defines the Utility."""

    def getConfiguration(self, context=None, field=None, request=None):
        """Get the configuration based on the control panel settings and the field settings.
        request can be provide for translation purpose."""


class IProjekktorProvider(I):
    """ marker interface for classes implementing a Projekktor proxy """

class IProjekktorMedia(I):

    def isAudio():
        """ Is this media audio? """

    def isVideo():
        """ Is this media audio? """

    def getFilepath():
        """ Filepath of this media """

    def getAlternativeFilepaths():
        """ Alternative filepaths of this media """

    def getTitle():
        """ Title of this video """

    def getDescription():
        """ Description of this video """

    def getMimetype():
        """ The mimetype of this object """

    def getWidth():
        """ Display width of this video """

    def getHeight():
        """ Display height of this video """



