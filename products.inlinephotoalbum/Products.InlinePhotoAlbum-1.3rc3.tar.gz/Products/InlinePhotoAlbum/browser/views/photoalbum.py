from DateTime import DateTime
from Acquisition import aq_inner

from zope.i18nmessageid import MessageFactory

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

class InlinePhotoAlbum(BrowserView):
    """ A view for showing a photoalbum
    """
    title = 'Photo Album'

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getPhotos(self):
        """ Get the photos 
        """
        context = aq_inner(self.context)
        if context.portal_type == 'Topic':
            queryMethod = context.queryCatalog
        else:
            queryMethod = context.getFolderContents

        result = queryMethod({'portal_type':('Image',)})
        return result

