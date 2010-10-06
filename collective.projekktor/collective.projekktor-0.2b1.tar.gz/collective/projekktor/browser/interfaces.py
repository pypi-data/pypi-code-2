from zope.interface import Interface as I 

from plone.portlets.interfaces import IPortletDataProvider

from zope.schema import Text,TextLine,List

from zope.viewlet.interfaces import IViewletManager

class IProjekktorControlPanelForm(I):
    """Projekktor Control Panel Form"""

class IProjekktorViewletManager( IViewletManager ):
    pass

class IProjekktorTesterPortlet(IPortletDataProvider):
    """ Projekktor tester portlet """
    tester_textline = TextLine(
        title=u"Text line",
        description=u"A test textline",
        required=False,
        readonly=False
        )    

class IProjekktorPortlet(IPortletDataProvider):
    """ Projekktor portlet """

    filepath = TextLine(
        title=u"Filepath",
        description=u"Path to the media file",
        required=False,
        readonly=False
        )    

    alternativeFilepaths = List(
        title=u"Alternative filepaths"
        ,description=u"Paths to alternative media files"
        ,required=False
        ,readonly=False
        ,value_type=TextLine()
        ,default=[]
        )    

    mediaWidth = TextLine(
        title=u"Media width",
        description=u"Width to display this media",
        required=False,
        readonly=False
        )    

    mediaHeight = TextLine(
        title=u"Media height",
        description=u"Height to display this media",
        required=False,
        readonly=False
        )    


    mediaPoster = TextLine(
        title=u"Media poster",
        description=u"Poster to display this media",
        required=False,
        readonly=False
        )    



    
