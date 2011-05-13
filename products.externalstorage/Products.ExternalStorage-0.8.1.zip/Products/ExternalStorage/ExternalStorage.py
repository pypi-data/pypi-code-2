"""External Storage for Archetypes.

Implements a filesystem based storage for archetypes fields.
"""

import os
import shutil

from Globals import INSTANCE_HOME
from StringIO import StringIO

from Acquisition import aq_base
from AccessControl import ClassSecurityInfo

from OFS.Image import File
from ZODB.PersistentMapping import PersistentMapping

from Products.CMFCore.utils import getToolByName

from Products.Archetypes.utils import shasattr
from Products.Archetypes.Storage import StorageLayer
from Products.Archetypes.interfaces.layer import ILayer
from Products.Archetypes.interfaces.field import IObjectField
from Products.ATContentTypes.content.base import cleanupFilename

from logging import ERROR
from Products.ExternalStorage.utils import log
from Products.ExternalStorage.utils import implementedOrProvidedBy

from Products.ExternalStorage.config import HAS_ITERATOR
from Products.ExternalStorage.config import ENVIRONMENT_VARIABLE
from Products.ExternalStorage.interfaces import IExternalStorage
from Products.ExternalStorage.filewrapper import FileWrapper


class ExternalStorage(StorageLayer):
    """Stores data as an external file.

    It gets stored in var/<configureddir>/<path>
    For now they all go into one file repository without directories.
    Archived versions will be stored in var/<configureddir>/ARCHIVE_PREFIX/<path>
    """

    __implements__ = (IExternalStorage, ILayer)

    security = ClassSecurityInfo()

    def __init__(self, prefix='files', archive=False, rename=False, suffix='',
                 path_method='getExternalPath'):
        """Initializes default values.
        """
        self.prefix = prefix
        self.archive = archive
        self.rename = rename
        self.renaming = False
        self.suffix = suffix
        self.path_method = path_method

    #
    # Storage API
    #

    security.declarePrivate('initializeInstance')
    def initializeInstance(self, instance, item=None, container=None):
        """
        - Check if storage isn't already initialized.
        - Code to initialize the storage at the instance.
        - Code to repopulate fields when copy or rename/cut instance.
        """
        # Keep backward compatibility with previous version
        self.migrate(instance)
        #if item is None:
        #    # Avoid double call from BaseObject.py(150)initializeLayers()
        #    return
        if not self.isInitialized(instance):
            self.initializeStorage(instance)
        else:
            path = '/'.join(instance.getPhysicalPath())
            # If path is different, then we have a copy or rename/cut
            if self.getInstancePath(instance) != path:
                self.setInstancePath(instance)
                # If we have no temp data yet, then this is a copy
                # operation, otherwise it's a rename/cut
                if not self.hasTempData(instance):
                    self.setTempData(instance)
            if self.hasTempData(instance):
                temp = self.getTempData(instance)
                self.renaming = True
                for name, value in temp.items():
                    # Update the filename
                    path = self.getFileSystemPath(instance, name)
                    filename = os.path.basename(path)
                    value.filename = filename
                    instance.getField(name).set(instance, value)
                self.renaming = False
                self.cleanTempData(instance)

    security.declarePrivate('cleanupInstance')
    def cleanupInstance(self, instance, item=None, container=None):
        """
        - Remove filesystem structure.
        """
        # XXX Add code to remove filesystem structure
        pass

    def initializeField(self, instance, field):
        """
        - Code to initialize field with default value.
        """
        name = field.getName()
        if not self.hasStorageItem(instance, name):
            self.set(name, instance, field.getDefault(instance))

    security.declarePrivate('cleanupField')
    def cleanupField(self, instance, field, **kwargs):
        """
        - Save storage fields when copy/rename/move instance.
        - Remove file from filesystem.
        """
        name = field.getName()
        self.unset(name, instance, **kwargs)
        path = self.getFilepath(instance, name)
        # In case of images we should do a shutil.rmtree() of the parent
        if path.endswith('/image') and os.path.exists(path[:-6]):
            shutil.rmtree(path[:-6])
        elif os.path.exists(path):
            os.remove(path)

    security.declarePrivate('get')
    def get(self, name, instance, **kwargs):
        """
        - Check if storage already is initialized.
        - Get wrapped data from storage.
        """
        if not self.isInitialized(instance):
            return
        filepath = self.getFilepath(instance, name)
        filename = self.getFilename(instance, name)
        mimetype = self.getContentType(instance, name)
        content_class = self.getContentClass(instance, name)
        kwargs = {
            'name': name,
            'filepath': filepath,
            'filename': filename,
            'mimetype': mimetype,
            'content_class': content_class,
        }
        if not os.path.exists(filepath):
            f = StringIO('')
        else:
            f = open(filepath, 'rb')

        wrapper = FileWrapper(f, **kwargs)

        if kwargs.get('useIterator', None) is not None and HAS_ITERATOR:
            return wrapper.filestream()
        else:
            return wrapper.getOFS()

    security.declarePrivate('set')
    def set(self, name, instance, value, **kwargs):
        """
        - Check if storage already is initialized.
        - Process rename action.
        - Set field data into storage.
        """
        if not self.isInitialized(instance):
            return
        mimetype = kwargs.get('mimetype', 'application/octet-stream')
        filename = getattr(value, 'filename', '')
        if filename:
            filename = cleanupFilename(filename.split('\\')[-1])
            if self.rename and not self.renaming and filename != instance.getId():
                plone_utils = getToolByName(instance, 'plone_utils')
                plone_utils.contentEdit(instance, id=filename)
        filepath = self.getFileSystemPath(instance, name)
        item = PersistentMapping()
        item.setdefault('data', value)
        item.setdefault('filepath', filepath)
        item.setdefault('mimetype', mimetype)
        item.setdefault('filename', filename)
        self.setStorageItem(instance, name, item)

    security.declarePrivate('unset')
    def unset(self, name, instance, **kwargs):
        """
        - Save data into temp area
        """
        self.setTempData(instance, name)

    #
    # Private Methods
    #

    # Temp Data handling

    security.declarePrivate('hasTempData')
    def hasTempData(self, instance):
        """Checks if ES storage has temp data.
        """
        UID = instance.UID()
        return shasattr(self, '_v_temp') and self._v_temp.has_key(UID)

    security.declarePrivate('cleanTempData')
    def cleanTempData(self, instance):
        """Removes temp data from ES storage.
        """
        UID = instance.UID()
        if shasattr(self, '_v_temp') and self._v_temp.has_key(UID):
            del self._v_temp[UID]

    security.declarePrivate('getTempData')
    def getTempData(self, instance):
        """Returns the temp data from ES storage.
        """
        return self._v_temp.get(instance.UID())

    security.declarePrivate('setTempData')
    def setTempData(self, instance, item=None):
        """Sets temp data into ES storage.
        """
        if not shasattr(self, '_v_temp'):
            self._v_temp = {}
        UID = instance.UID()
        if not self._v_temp.has_key(UID):
            self._v_temp[UID] = {}
        temp = self._v_temp[UID]
        fields = self.getStorageFields(instance)
        for field in fields:
            name = field.getName()
            value = field.get(instance)
            temp.update({name: value})

    # Storage handling

    security.declarePrivate('isInitialized')
    def isInitialized(self, instance):
        """Checks if the ES storage area is already initialized.
        """
        return shasattr(instance, '_es')

    security.declarePrivate('initializeStorage')
    def initializeStorage(self, instance):
        """Initializes the ES storage area.
        """
        instance._es = PersistentMapping()
        self.setInstancePath(instance)

    security.declarePrivate('hasStorageItem')
    def hasStorageItem(self, instance, name):
        """Checks if ES storage area has an item.
        """
        return instance._es.has_key(name)

    security.declarePrivate('setStorageItem')
    def setStorageItem(self, instance, name, value):
        """Sets an item into ES storage area.
        """
        data = value.pop('data')

        if implementedOrProvidedBy(IObjectField, data):
            new_data = data.getRaw(instance)
        elif isinstance(data, File):
            new_data = data.data
        else:
            new_data = str(data)
        if new_data is None:
            new_data = ''

        data = StringIO(new_data)

        filepath = value.get('filepath')
        try:
            self.checkDirs(filepath)
            out = open(filepath, 'wb')
            blocksize = 2<<16
            block = data.read(blocksize)
            out.write(block)
            while len(block) == blocksize:
                block = data.read(blocksize)
                out.write(block)
            data.seek(0)
            out.close()
        except IOError, e:
            log('copy of external file failed', text=str(e), log_level=ERROR)
            raise

        instance._es.update({name: value})

    security.declarePrivate('getStorageItem')
    def getStorageItem(self, instance, name):
        """Returns an item from the ES storage area.
        """
        return instance._es.get(name)

    # Shortcuts to access ES storage area for a given fieldname

    security.declarePrivate('getFilepath')
    def getFilepath(self, instance, name):
        """Returns the filepath from field.
        """
        item = self.getStorageItem(instance, name)
        filepath = item.get('filepath')
        return filepath

    security.declarePrivate('getFilename')
    def getFilename(self, instance, name):
        """Returns the filename from field.
        """
        item = self.getStorageItem(instance, name)
        filename = item.get('filename', '')
        return filename

    security.declarePrivate('getContentType')
    def getContentType(self, instance, name):
        """Returns the content type from field.
        """
        item = self.getStorageItem(instance, name)
        mimetype = item.get('mimetype', 'plain/text')
        return mimetype

    # Path handling

    security.declarePrivate('getInstancePath')
    def getInstancePath(self, instance):
        """Returns the instance path from storage.
        """
        return instance._es.get('_es_path')

    security.declarePrivate('setInstancePath')
    def setInstancePath(self, instance):
        """Saves the instance path into storage.
        """
        path = '/'.join(instance.getPhysicalPath())
        instance._es.update({'_es_path': path})

    security.declarePrivate('getRootPath')
    def getRootPath(self):
        """Returns the file system root path for the storage.

        This is usually the 'var' directory in the INSTANCE_HOME.

        You can also override this by setting a environment variable
        which is then used instead.
        """
        root = INSTANCE_HOME + '/var'
        if os.environ.has_key(ENVIRONMENT_VARIABLE):
            root = os.environ.get(ENVIRONMENT_VARIABLE)
        path = os.path.join(root, self.prefix)
        path = os.path.normpath(path)
        return path

    security.declarePrivate('getFileSystemPath')
    def getFileSystemPath(self, instance, item):
        """Returns the file system path (with filename) where to store
        a instance field.
        """
        if shasattr(instance, self.path_method):
            method = getattr(instance, self.path_method)
            path = method(item)
        else:
            pu = getToolByName(instance, 'portal_url')
            relative = pu.getRelativeContentPath(instance)
            path = '/'.join(relative)
            # When the instance has multiple fields with ExternalStorage
            # and the storages are compatible, then each file receives the
            # field name and are stored inside the instance folder
            if len(self.getStorageFields(instance)) > 1:
                path = os.path.join(path, item)
            else:
                # also use the field name if this is an ImageField with scales
                # This will result in a directory with a file for each scale
                field = self.getField(instance, item)
                ftype = getattr(field, 'type', None)
                if ftype == 'image' and field.getAvailableSizes(instance):
                    path = os.path.join(path, item)
            path = path + self.suffix
        root = self.getRootPath()
        if path.startswith('/'):
            path = path[1:]
        path = os.path.join(root, path)
        return path

    # Utilities

    security.declarePrivate('getField')
    def getField(self, instance, name):
        """Returns the field we are defined for
        """
        field = instance.Schema().getField(name)
        if field is None and '_' in name:
            # Possibly image scales, see if we can find the image
            for f in self.getStorageFields(instance):
                if not f.type == 'image':
                    continue
                fname = f.getName()
                if name.startswith(fname + '_'):
                    scale = name[len(fname) + 1:]
                    if scale in f.getAvailableSizes(instance):
                        # Bingo
                        return f
        return field

    security.declarePrivate('getContentClass')
    def getContentClass(self, instance, name):
        """Returns the 'content_class' attribute of the field
        """
        field = self.getField(instance, name)
        return getattr(field, 'content_class', None)

    security.declarePrivate('getStorageFields')
    def getStorageFields(self, instance):
        """Returns all fields which uses compatible storages.
        """
        fields = instance.Schema().fields()
        return [f for f in fields if
                implementedOrProvidedBy(IObjectField, f) and
                self.isCompatibleWithStorage(f.getStorage())]

    security.declarePrivate('isCompatibleWithStorage')
    def isCompatibleWithStorage(self, storage):
        """Checks if a given schema is compatible with current one.

        Two storages are considered compatible when they share the
        same prefix and path_method.
        """
        return shasattr(storage, 'prefix') and \
               shasattr(storage, 'path_method') and \
               self.prefix == storage.prefix and \
               self.path_method == storage.path_method

    security.declarePrivate('checkDirs')
    def checkDirs(self, path):
        """Makes sure the directory structure exists.
        """
        data_dir = os.path.dirname(path)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    security.declarePrivate('migrate')
    def migrate(self, instance):
        """Migrates data from the old format to the new one.
        """
        if shasattr(instance, '_es_initialized'):
            obj = aq_base(instance)
            filename = getattr(obj, '_es_filename', '')
            filepath = getattr(obj, '_es_filepath', '')
            mimetype = getattr(obj, '_es_mimetype', '')
            fields = self.getStorageFields(instance)
            name = fields[0].getName()
            item = PersistentMapping()
            item.setdefault('filepath', filepath)
            item.setdefault('mimetype', mimetype)
            item.setdefault('filename', filename)
            instance._es.update({name: item})
            for attr in ['_es_initialized', '_es_filename',
                         '_es_filepath', '_es_mimetype']:
                delattr(obj, attr)
