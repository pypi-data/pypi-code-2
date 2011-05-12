from os.path import isfile
from shutil import copyfileobj
from os import name as os_name
from StringIO import StringIO

from zope.interface import implements
from zope.component import adapts

from Products.CMFDefault.interfaces import IFile

from plone.app.blob.interfaces import IBlobbable

import ZPublisher.HTTPRequest

class BlobbableFileUpload(object):
    """adapts for ZPublisher FileUpload to work with blobs"""
    implements(IBlobbable)
    adapts(ZPublisher.HTTPRequest.FileUpload)
    
    def __init__(self, context):
        self.context = context
        
    def mimetype(self):
        return self.context.headers['mime-type']
        
    def filename(self):
        return self.context.filename

    def feed(self, blob):
        """ see interface ... """
        blob.open('w').write(self.context.read())
                
class BlobbableFile(object):
    """ adapter for FileUpload objects to work with blobs """
    implements(IBlobbable)
    adapts(IFile)

    def __init__(self, context):
        self.context = context
        self._name = context.filename

    def mimetype(self):
        return self.context.content_type

    def filename(self):
        # HACK! This only seems to get triggered during initial creation from createObject
        if self._name == 'downloadableFile': 
            return ''
        return self._name

    def feed(self, blob):
        """ see interface ... """
        file_ = StringIO(self.context.data)
        blob.open('w').write(file_.read())

