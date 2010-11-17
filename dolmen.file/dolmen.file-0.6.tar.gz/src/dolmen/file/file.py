# -*- coding: utf-8 -*-
"""FileChunk is taken from the zope.app.file package.
Copyright Zope Foundation.
"""

import transaction
from dolmen.file import IDataChunk, FileChunk, clean_filename
from persistent import Persistent
from zope import schema
from zope.interface import Interface, implements
from zope.contenttype import guess_content_type
from zope.schema.fieldproperty import FieldProperty

# set the size of the chunks
MAXCHUNKSIZE = 1 << 16


class INamedFile(Interface):
    """Defines a file that is aware of its filename.
    """
    filename = schema.TextLine(
        title=u"Name of file",
        required=True,
        default=u'',
        )

    contentType = schema.BytesLine(
        title=u'Content Type',
        description=u'The content type identifies the type of data.',
        default='',
        required=False,
        missing_value='',
        )

    data = schema.Bytes(
        title=u'Data',
        description=u'The actual content of the object.',
        default='',
        missing_value='',
        required=False,
        )

    size = schema.Int(
        title=u"Size",
        description=u"Size in bytes",
        readonly=True,
        required=True,
        )


class NamedFile(Persistent):
    """A simple INamedFile implementation that can guess the content type
    from the value and the filename.
    """
    implements(INamedFile)
    filename = FieldProperty(INamedFile['filename'])

    def __init__(self, data='', contentType='', filename=None):
        self.data = data
        if filename is not None:
            self.filename = clean_filename(filename)
        if not contentType and filename:
            # If we handle large files, we don't want them read just
            # to guess the content type. We provide only the filename.
            self.contentType, enc = guess_content_type(name=filename)
        else:
            self.contentType = contentType

    @apply
    def data():
        """Property in charge of setting and getting the file data.
        """

        def get(self):
            if IDataChunk.providedBy(self._data):
                return str(self._data)
            return self._data

        def set(self, data):
            # Handle case when data is a string
            if isinstance(data, unicode):
                data = data.encode('UTF-8')

            if isinstance(data, str):
                self._data, self._size = FileChunk(data), len(data)
                return

            # Handle case when data is None
            if data is None:
                raise TypeError('Cannot set None data on a file.')

            # Handle case when data is already a FileChunk
            if isinstance(data, FileChunk):
                size = len(data)
                self._data, self._size = data, size
                return

            # Handle case when data is a file object
            seek = data.seek
            read = data.read

            seek(0, 2)
            size = end = data.tell()

            if size <= 2 * MAXCHUNKSIZE:
                seek(0)
                if size < MAXCHUNKSIZE:
                    self._data, self._size = read(size), size
                    return
                self._data, self._size = FileChunk(read(size)), size
                return

            # Make sure we have an _p_jar, even if we are a new object, by
            # doing a sub-transaction commit.
            transaction.savepoint(optimistic=True)

            jar = self._p_jar

            if jar is None:
                # Ugh
                seek(0)
                self._data, self._size = FileChunk(read(size)), size
                return

            # Now we're going to build a linked list from back
            # to front to minimize the number of database updates
            # and to allow us to get things out of memory as soon as
            # possible.
            next = None
            while end > 0:
                pos = end - MAXCHUNKSIZE
                if pos < MAXCHUNKSIZE:
                    pos = 0 # we always want at least MAXCHUNKSIZE bytes
                    seek(pos)
                    data = FileChunk(read(end - pos))

                # Woooop Woooop Woooop! This is a trick.
                # We stuff the data directly into our jar to reduce the
                # number of updates necessary.
                jar.add(data)

                # This is needed and has side benefit of getting
                # the thing registered:
                data.next = next

                # Now make it get saved in a sub-transaction!
                transaction.savepoint(optimistic=True)

                # Now make it a ghost to free the memory.  We
                # don't need it anymore!
                data._p_changed = None

                next = data
                end = pos

            self._data, self._size = next, size
            return

        return property(get, set)

    @property
    def size(self):
        return self._size
