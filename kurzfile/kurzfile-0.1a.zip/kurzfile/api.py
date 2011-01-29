# -*- coding:utf-8 -*-
#
# kurzfile/__init__.py
#
"""A package for handling Kurzweil K-series object files."""

__all__ = [
    'Kurzfile',
    'KurzfileHeader',
    'KurzfileBlock',
    'KurzfileObject',
    'ParseError'
]

# standard library modules
import logging

from os.path import basename, dirname, getsize
from struct import unpack_from

# package-specific modules
from kurzfile.util import xlate_object_id
from kurzfile.constants import *


log = logging.getLogger(__name__)

# custom exceptions
class ParseError(Exception):
    pass


# utility functions
def parse_header(data):
    """Parse the 32-byte header of a KRZ file, return a KurzfileHeader istance.
    """
    if len(data) < 32:
        raise ValueError(
            "Header size too small (%i bytes). Must be 32 bytes." % len(data))
    if data[:4] not in KNOWN_FILETYPES:
        raise ValueError("Unknown file type ID (%r)." % data[:4])

    header = KurzfileHeader()
    header.file_type = data[:4]
    header.obj_data_len = unpack_from('>I', data, 4)[0]
    header.smpl_data_len = unpack_from('>I', data, 8)[0]
    header.file_seq_no = unpack_from('>I', data, 12)[0]
    header.multifile = header.file_seq_no != 0

    header.os_version = unpack_from('>I', data, 16)[0]
    header.model_id = unpack_from('BBBB', data, 20)

    return header

# API classes
class Kurzfile(object):
    """Represent a KRZ file and all the data blocks and objects in it."""
    def __init__(self, filename=None):
        self.header = None
        self.blocks = []
        if filename:
            self.parse_file(filename)
        else:
            self.filename = None

    def parse_file(self, filename):
        """Parse a KRZ file by reading all object data blocks."""
        self.filename = filename
        self.filesize = getsize(filename)
        kurzfile = open(filename, 'rb')

        try:
            hdr = self.header = parse_header(kurzfile.read(32))
            log.debug("File '%s', size %i",
                      self.filename, self.filesize)
            log.debug("Header: %s", hdr)

            object_data = kurzfile.read(hdr.obj_data_len)
            log.debug("Parsing object data...")
            self.blocks = self.parse_object_data(object_data)
        except (IOError, OSError, ValueError) as exc:
            raise ParseError(str(exc))
        finally:
            kurzfile.close()

    def parse_object_data(self, data):
        """Parse the object data portion and extract all data blocks."""
        data_len = self.header.obj_data_len
        offset = 0; block_count = 0
        while True:
            if offset+4 >= len(data):
                if len(data) < data_len - 32:
                    log.warning("Truncated object data. Expected %i bytes, "
                        "Got only %i bytes.", data_len, len(data))
                break

            blocksize = abs(unpack_from('>i', data, offset)[0])

            if blocksize == 0:
                log.debug("Blocksize == 0: end of object data")
                break

            block_count += 1
            log.debug("Found data block of %i bytes length.", blocksize)

            yield KurzfileBlock(
                self, blocksize, data[offset+4:offset+blocksize])

            offset += blocksize
            # adjust offset to four-byte block boundary
            offset += offset % 4

        log.debug("Found %i data block(s) in object data.", block_count)

    def parse_typeid(self, typeid):
        """Separate a typeid field from the object data into type code and ID.
        """
        typecode, id = typeid
        if typecode >= 0x90:
            # XXX: Not sure, if this is valid for very incarnation of the K.
            # Should we really do this unconditionally?
            #if self.header.model_id[0] >= 3:
            if True:
                id = ((typecode & 3) << 8) | id
                typecode = typecode & 252
        return typecode, id

    def list_objects(self, stream=None, listformat='pretty', format=None,
            extrafields=None):
        """Print a listing of all objecs to given file-like 'stream' object.

        'listformat' can 'pretty' or 'csv'. The first generates a text listing,
        formatted for display, the second a comma-separated value list, ready
        to be imported into a spreadsheed application or database.

        'format', if given, must be a string containg string formatting
        placeholders for the object data to be printed in each line. The default
        line format is::

            "%(id)08i %(type_name)-18s %(name)-18s %(size)12s"

        extrafields, if given, must be a dictionary, whose keys match any
        placeholder names in the line format string, which do not respond to
        an attribute name of KurzfileObject instances.

        """
        if stream is None:
            stream = sys.stdout
        if listformat == 'pretty':
            print >>stream, "%-4s%-19s %-19s%13s" % (
                'ID', 'Type', 'Name', 'Size (bytes)')
            print >>stream, "-" * 55
        elif listformat == 'csv':
            if format is None:
                format = ('%(id)03i;"%(type_name)s";"%(name)s";'
                    '%(size)i;"%(filename)s";%(filesize)s;"%(path)s"')

            if not extrafields:
                extrafields = dict(
                    filename=basename(self.filename),
                    filesize=self.filesize,
                    path=dirname(self.filename))
        else:
            raise ValueError("List format '%s' not supported." % listformat)

        for block in self.blocks:
            for obj in block.objects:
                print >>stream, obj.list(format, extrafields)

        if listformat == 'pretty':
            print >>stream

class KurzfileHeader(object):
    """Represent the 2-byte hader of a KRZ file."""
    #def __init__(self):
    #    pass
    fields = (
        ('file_type', 'File type', str),
        ('multifile', 'Part of a multifile set?',
            lambda x: 'yes' if x else 'no'),
        ('file_seq_no', '# in sequence', int),
        ('model_id', 'Model ID', repr),
        ('os_version', 'OS version', lambda x: "%.2f" % (x/100.0,)),
        ('obj_data_len', 'Size of object data', int),
        # XXX: this is not accurate for most (non-multipart) files
        #('smpl_data_len', 'Size of sample data', int)
    )

    def __str__(self):
        """Return header data nicely formatted."""
        s = ''
        for k, desc, conv in self.fields:
            s += "%s: %s\n" % (desc, conv(getattr(self, k)))
        return s


class KurzfileBlock(object):
    """Represent a data nlcok in a KRZ file.

    Data blocks are containers for the actual objects in a KRZ file.

    """
    def __init__(self, kurzfile, size=0, data=""):
        self.kurzfile = kurzfile
        self.size = size
        self.data = data
        self.objects = self.parse(data)

    def parse(self, data):
        """Parse a data block and yield all contained objects."""
        offset = 0; obj_count = 0
        while True:
            if offset >= self.size - 4:
                break

            typeid = unpack_from('BB', data, offset)
            size = unpack_from('>H', data, offset + 2)[0]
            d_offset = unpack_from('>H', data, offset + 4)[0]
            #log.debug("Data offset: %r", data_offset)
            name = unpack_from('%is' % (d_offset - 2,), data, offset + 6)[0]
            name = name.split('\0', 1)[0]

            type, id = self.kurzfile.parse_typeid(typeid)
            obj_count += 1
            log.debug("Object with typeid %s,%s (type=%s, ID %i) found.",
                hex(typeid[0]), hex(typeid[1]), type, id)


            yield KurzfileObject(type, id, name, size,
                data[offset + 4 + d_offset:offset + size])

            offset += size
            # adjust offset to four-byte block-boundary
            offset += offset % 4

        log.debug("Found %i object(s) in this block.", obj_count)


class KurzfileObject(object):
    """Represent a Kurzweil K-series object."""

    def __init__(self, type=None, id=None, name=None, size=None, data=None):
        self.type = type
        self._id = id
        self.name = name
        self.size = size
        self.data = data

    def __str__(self):
        return self.list()

    def list(self, format=None, extrafields=None):
        """Return a line with formatted object information.

        For the 'format' and 'extrafields' arguments see the 'list_objects'
        method of the 'Kurzfile' class.

        """
        if format is None:
            format = "%(id)08i %(type_name)-18s %(name)-18s %(size)12s"
        data = dict()
        for attr in ('id', 'type', 'type_name', 'name', 'size'):
            data[attr] = getattr(self, attr, None)
        if extrafields:
            data.update(extrafields)
        return format % data

    @property
    def id(self):
        return xlate_object_id(self.type, self._id)

    @property
    def type_name(self):
        return OBJECT_TYPES.get(self.type, "0x%X" % self.type)
