from Globals import InitializeClass

from Acquisition import Explicit
from Acquisition import aq_parent
from AccessControl import ClassSecurityInfo

from OFS.Image import getImageInfo
from OFS.Image import File as OFSFile
from OFS.Image import Image as OFSImage

from ZPublisher.Iterators import filestream_iterator


class FileWrapper:
    """Wraps a file object in a wrapper to add some features.

    * len() is very efficient because it is using seek/tell to get the file size
    * filestream() returns a Zope filestream iterator (needs the filepath kwargs)
    * getOFS returns an OFS File or Image instance depending on the mimetype and
      also adds height and width to the returned instance
      (requires name, mimetype and filename in kwargs)
    * get_size is a compatibility method and alias for len()
    """

    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')
    security.declareObjectPublic()

    def __init__(self, file, **kwargs):
        self.file = file
        self.size = None
        self._ofs = None
        self.__dict__.update(kwargs)
        if self.mimetype and self.mimetype.startswith('image'):
            self.isImage = True
        else:
            self.isImage = False

    def __getstate__(self):
        raise RuntimeError, "Should never happen!"

    def __setstate__(self, value):
        raise RuntimeError, "Should never happen!"

    def __len__(self):
        if self.size is None:
            f = self.file
            f.seek(0, 2)
            size = f.tell()
            f.seek(0)
            if not size:
                size = 0
            self.size = int(size)
        return self.size

    def __str__(self):
        f = self.file
        f.seek(0)
        data = f.read()
        f.seek(0)
        return data

    def __getattr__(self, key):
        # special cases for OFSImage
        if key in ('width', 'height', 'tag') and self.isImage:
            ofs = self.getOFS()
            return getattr(ofs, key)
        # special cases for OFSFile and OFSImage
        if key is 'data':
            ofs = self.getOFS()
            return getattr(ofs, key)
        return getattr(self.file, key)

    def __nonzero__(self):
        return len(self)

    def __cmp__(self, other):
        return cmp(len(self), len(other))

    # OFS.Image aliases

    def get_size(self):
        return len(self)

    def getSize(self):
        return len(self)

    def getContentType(self):
        return self.mimetype

    def getFilename(self):
        return self.filename

    def getOFS(self):
        if self._ofs is not None:
            return self._ofs
        # The Archetypes Field can specify a OFS.File-based content class
        klass = getattr(self, 'content_class', None)
        if klass is None:
            klass = self.isImage and OFSImage or OFSFile
        else:
            # If the field specified an image-based class, we are an image.
            self.isImage = issubclass(klass, OFSImage)
        ofs = klass(id=self.name, title='', file=self.file,
                    content_type=self.mimetype)
        ofs.filename = self.filename
        self.file.seek(0)
        if self.isImage:
            self.width = ofs.width or None
            self.height = ofs.height or None
        self._ofs = ofs
        return ofs

    def filestream(self):
        return filestream_iterator(self.filepath, 'rb')

    def getvalue(self):
        return str(self)

InitializeClass(FileWrapper)
