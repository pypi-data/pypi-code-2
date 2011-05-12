from OFS.Image import File
from StringIO import StringIO

from zope.interface import directlyProvides
from zope.interface import implements

from plone.app.blob.field import BlobWrapper as BlobWrapper_
from plone.app.blob.field import BlobField as BlobField_
from plone.app.blob.field import ObjectField

from plone.app.blob.interfaces import IBlobbable

from Products.CMFDefault.interfaces import IFile
from Products.PloneSoftwareCenter.storage.interfaces import IPSCFileStorage

class BlobWrapper(BlobWrapper_):
    def manage_upload(self, data):
        if isinstance(data, basestring):
            data = StringIO(data)
        blobbable = IBlobbable(data)
        blobbable.feed(self.getBlob())

    def __len__(self):
        return self.get_size()

    def seek(self, *args, **kw):
        pass
    
    def tell(self):
        pass

    def read(self, size):
        return self.data
        

class BlobField(BlobField_):
    def set(self, instance, value, **kwargs):
        """ use input value to populate the blob and set the associated
            file name and mimetype """
        if value == "DELETE_FILE":
            ObjectField.unset(self, instance, **kwargs)
            return
        # create a new blob instead of modifying the old one to
        # achieve copy-on-write semantics.
        blob = BlobWrapper()
        if isinstance(value, basestring):
            # make StringIO from string, because StringIO may be adapted to Blobabble
            value = StringIO(value)
        if value is not None:
            blobbable = IBlobbable(value)
            blobbable.feed(blob.getBlob())
            blob.setContentType(blobbable.mimetype())
            blob.setFilename(blobbable.filename())
        ObjectField.set(self, instance, blob, **kwargs)
        self.fixAutoId(instance)
 

class BlobStorage(object):
    implements(IPSCFileStorage)
    title = u"Blob"
    description = u"store releases using ZODB Blob Support (EXPERIMENTAL)"
    
    def __init__(self, context):
        self.context = context

    def _getStorage(self, name, instance):
        if not hasattr(instance, '_bs'):
            field = BlobField()
            setattr(instance, '_bs', field)
    
        return getattr(instance, '_bs')

    def get(self, name, instance, **kwargs):
        field = self._getStorage(name, instance)
        
        return field.get(instance, **kwargs)

    def set(self, name, instance, value, **kwargs):
        if isinstance(value, File):
            directlyProvides(value, IFile)
            value.filename = name
        
        field = self._getStorage(name, instance)
        return field.set(instance, value, **kwargs)

    def unset(self, name, instance, **kwargs):
        field = self._getStorage(name, instance)
        return field.unset(instance, **kwargs)


