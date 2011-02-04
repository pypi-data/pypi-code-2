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
import csv
import logging

from operator import attrgetter
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
    """Parse 32-byte header of a KRZ file, return a KurzfileHeader istance.
    """
    if len(data) < 32:
        raise ValueError(
            "Header size too small (%i bytes). Must be 32 bytes." % len(data))
    if data[:4] not in KNOWN_FILETYPES:
        raise ValueError("Unknown file type ID (%r)." % data[:4])

    header = KurzfileHeader()
    header.file_type = data[:4]
    header.object_data_size = unpack_from('>I', data, 4)[0]
    header.sample_data_size = unpack_from('>I', data, 8)[0]
    header.file_seq_no = unpack_from('>I', data, 12)[0]
    header.multifile = header.file_seq_no != 0

    header.os_version = unpack_from('>I', data, 16)[0]
    header.model_id = unpack_from('BBBB', data, 20)

    return header


# API classes
class Kurzfile(object):
    """Represent a KRZ file and all the data blocks and objects in it."""

    def __init__(self, filename=None, strict=False):
        self.header = None
        self.blocks = []
        self.strict = strict
        if filename:
            self.parse_file(filename)
        else:
            self.filename = None

    @property
    def objects(self):
        for block in self.blocks:
            for obj in block.objects:
                yield obj

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

            object_data = kurzfile.read(hdr.object_data_size)
            obj_data_size = len(object_data)

            # some files include the 32-byte header in the object data size
            if hdr.object_data_size == obj_data_size + 32:
                hdr.object_data_size -= 32

            if obj_data_size < hdr.object_data_size:
                msg = ("Truncated object data. Expected %i bytes, read only %i "
                    "bytes before end-of-file." % (
                    hdr.object_data_size, object_data_size))

                if self.strict:
                    raise ParseError(msg)

                log.warning(msg)
                hdr.object_data_ize = object_data_size

            if obj_data_size == self.filesize - 32 and hdr.sample_data_size != 0:
                log.debug("Bogus sample data size in header. Setting it to zero.")
                hdr.sample_data_size = 0
                hdr.multifile = False
                hdr.file_seq_no = 0

            log.debug("Parsing object data...")
            self.blocks = self.parse_object_data(object_data)

            # sample data size in header is unreliabe,
            # we have to calculate it ourselves from the filesize
            log.debug("Calculating sample data size...")
            hdr.sample_data_offset = 32 + hdr.object_data_size
            hdr.sample_data_size = self.filesize - hdr.sample_data_offset
        except (IOError, OSError, ValueError) as exc:
            raise ParseError(str(exc))
        finally:
            kurzfile.close()

    def parse_object_data(self, data):
        """Parse the object data portion and extract all data blocks."""
        data_len = self.header.object_data_size
        offset = 0; block_count = 0
        while True:
            if offset+4 > len(data):
                if len(data) < data_len - 32:
                    msg = ("Truncated object data. Expected %i bytes, got only "
                           "%i bytes." % (data_len, len(data)))

                    if self.strict:
                        raise ParseError(msg)

                    log.warning(msg)

                break

            blocksize = abs(unpack_from('>i', data, offset)[0])

            if blocksize == 0:
                log.debug("Blocksize == 0: end of object data")
                break

            block_count += 1
            log.debug("Found data block header, block size: 0x%X ", blocksize)

            remaining_data = data[offset:]
            if blocksize >= len(remaining_data):
                msg = ("Truncated block data. Expected %i bytes, read only %i "
                    "bytes before end of data." % (
                    blocksize, len(remaining_data)))

                if self.strict:
                    raise ParseError(msg)

                log.warning(msg)
                blocksize = len(remaining_data)

            yield KurzfileBlock(self,
                blocksize, data[offset + 4:offset + blocksize])

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
            fields=None, sortby=None):
        """Print a listing of all objecs to given file-like 'stream' object.

        'listformat' can 'pretty' or 'csv'. The first generates a text listing,
        formatted for display, the second a semicolon-separated value list,
        ready to be imported into a spreadsheed application or database.

        'format', if given, must be a string containg string formatting
        placeholders for the object data to be printed in each line. This is
        only used for the 'pretty' lisformat. The default line format is::

            "%(type_name)-16s %(id)03i %(name)-18s %(size)12s"

        'fields', if given, must be a list or tuple of KurzFileObject attribute
        names, which are used to supply the values for the placeholders in the
        format string. The default matches the placeholders used in the default
        format string.

        'sortby' can be an attribute name or a list of attributes of
        KurzfileObjects to sort the object list by. If 'sortby' is None or not
        given, objects are listed in the order they appear in the file.

        """
        if stream is None:
            stream = sys.stdout
        if listformat == 'pretty':
            print >>stream, "%-16s %-3s %-12s %12s" % (
                'Type', 'ID', 'Name', 'Size (bytes)')
            print >>stream, "-" * 46
        elif listformat == 'csv':
            fileinfo = dict(
                filename=basename(self.filename),
                filesize=self.filesize,
                path=dirname(self.filename)
            )
            if not fields:
                fields = ('type_name', 'id', 'name', 'size', 'filename',
                    'filesize', 'path')
            csvwriter = csv.DictWriter(stream, fields, delimiter=';')
        else:
            raise ValueError("List format '%s' not supported." % listformat)

        if sortby:
            objects = sorted(self.objects, key=attrgetter(*sortby))
        else:
            objects = self.objects

        for obj in objects:
            if listformat == 'pretty':
                print >>stream, obj.list(format, fields)
            elif listformat == 'csv':
                data = obj.get_dict(fields)
                data.update(fileinfo)
                csvwriter.writerow(data)

        if listformat == 'pretty':
            print >>stream


class KurzfileHeader(object):
    """Represent the 2-byte hader of a KRZ file."""
    #def __init__(self):
    #    pass
    fields = (
        ('file_type', 'File type', str),
        ('model_id', 'Model ID', repr),
        ('os_version', 'OS version', lambda x: "%.2f" % (x/100.0,)),
        ('object_data_size', 'Object data size', int),
        ('multifile', 'Multifile set?',
            lambda x: 'yes' if x else 'no'),
        ('file_seq_no', 'No. in sequence', int),
        # XXX: this is not accurate for most (non-multipart) files
        ('sample_data_size', 'Size of sample data', int)
    )

    def __str__(self):
        """Return header data nicely formatted."""
        s = ''
        for k, desc, conv in self.fields:
            if k == 'file_seq_no' and not self.multifile:
                continue
            s += "%s: %s\n" % (desc, conv(getattr(self, k)))
        return s


class KurzfileBlock(object):
    """Represent a data nlcok in a KRZ file.

    Data blocks are containers for the actual objects in a KRZ file.

    """
    def __init__(self, kurzfile, size=0, data="", strict=False):
        self.kurzfile = kurzfile
        self.size = size
        self.data = data
        self.strict = strict
        self.objects = self.parse(data)

    def parse(self, data):
        """Parse a data block and yield all contained objects."""
        offset = 0; obj_count = 0
        while True:
            if offset + 4 >= self.size:
                break

            typeid = unpack_from('BB', data, offset)
            type, id = self.kurzfile.parse_typeid(typeid)
            log.debug("Object with typeid %s,%s (type=%s, ID %i) found.",
                hex(typeid[0]), hex(typeid[1]), type, id)

            size = unpack_from('>H', data, offset + 2)[0]

            if size == 0:
                log.debug("Object size == 0 => end of object data")
                break

            d_offset = unpack_from('>H', data, offset + 4)[0]
            log.debug("Size: %i; Data offset: %i", size, d_offset)

            # check sanity of object data
            remaining = len(data[offset:])
            if size > remaining:
                msg = ("Illegal object size value (%i) >= data size (%i)" % (
                    size, remaining))

                if self.strict:
                    raise ParseError(msg)

                log.warning(msg)
                size = remaining

            if d_offset >= size-2:
                msg = ("Illegal data offset value (%i) >= object size (%i)" % (
                    d_offset, size))
                if self.strict:
                    raise ParseError(msg)

                log.warning(msg)
            elif d_offset < 4:
                msg = "Illegal data offset value (%i), must >= 4." % d_offset

                if self.strict:
                    raise ParseError(msg)

                log.warning(msg)
            else:
                name = unpack_from('%is' % (d_offset - 2,), data, offset + 6)[0]
                name = name.split('\0', 1)[0]
                log.debug("Object name: %r", name)

                obj_count += 1


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

    def list(self, format=None, fields=None):
        """Return a line with formatted object information.

        For the 'format' and 'extrafields' arguments see the 'list_objects'
        method of the 'Kurzfile' class.

        """
        if format is None:
            format = "%(type_name)-16s %(id)03i %(name)-18s %(size)6s"
        if fields is None:
            fields = ('id', 'type', 'type_name', 'name', 'size')
        return format % self.get_dict(fields)

    def get_dict(self, fields):
        data = dict()
        for attr in fields:
            data[attr] = getattr(self, attr, None)
        return data

    @property
    def id(self):
        return xlate_object_id(self.type, self._id)

    @property
    def type_name(self):
        return OBJECT_TYPES.get(self.type, "0x%X" % self.type)
