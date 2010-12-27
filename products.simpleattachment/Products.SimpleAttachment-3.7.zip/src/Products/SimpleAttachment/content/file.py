from copy import deepcopy
from logging import getLogger
from zlib import compress, decompress
from zope.annotation.interfaces import IAnnotations
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View
from Products.ATContentTypes.content.file import ATFile
from Products.Archetypes.public import registerType, FileField
from Products.SimpleAttachment.config import PROJECTNAME

debug = getLogger(__name__).debug
key = 'transforms_cache'


class CachingFileField(FileField):
    """ extended version of AT's file-field support a transforms caching """

    def set(self, instance, value, **kwargs):
        annotations = IAnnotations(instance)
        if key in annotations:
            del annotations[key]
        return super(CachingFileField, self).set(instance, value, **kwargs)


def makeField(field):
    """ mostly copied from `Archetypes.Field.Field.copy` """
    cdict = dict(vars(field))
    cdict.pop('__name__')
    # Widget must be copied separatedly
    widget = cdict['widget']
    del cdict['widget']
    properties = deepcopy(cdict)
    properties['widget'] = widget.copy()
    return CachingFileField(field.getName(), **properties)


schema = ATFile.schema.copy()
schema['file'] = makeField(schema['file'])
schema['file'].index_method = 'indexData'


class FileAttachment(ATFile):
    """A file attachment"""

    portal_type = meta_type = 'FileAttachment'
    schema = schema
    security = ClassSecurityInfo()

    security.declareProtected(View, 'indexData')
    def indexData(self, mimetype=None):
        """ index accessor with caching of the result """
        if not mimetype == 'text/plain':
            return self.getFile()
        annotations = IAnnotations(self)
        if key in annotations:
            debug('using cached transforms value for %r', self)
            value = decompress(annotations[key])
        else:
            debug('getting transforms value for %r', self)
            value = self.getField('file').getIndexable(self)
            if value:
                annotations[key] = compress(value)
        return value

    def setFile(self, value):
        """ wrapper for "file" field mutator with cache invalidation """
        annotations = IAnnotations(self)
        if key in annotations:
            del annotations[key]
        return super(FileAttachment, self).setFile(value)


registerType(FileAttachment, PROJECTNAME)
