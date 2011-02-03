# -*- coding: utf-8 -*-
'''MongoDB GridFS storage back-end.'''

## Created: 2010-09-04 Guy K. Kloss <Guy.Kloss@aut.ac.nz>
##
## Copyright 2010 Guy K. Kloss
## Some rights reserved.
##
## http://www.aut.ac.nz/

__author__ = 'Guy K. Kloss <Guy.Kloss@aut.ac.nz>'
__date__ = '$Date: $'

import mimetypes
import pymongo
import bson
from bson import json_util
import gridfs

from matanui import config
from matanui import storerinterface
from matanui.exceptions import MataNuiStorerException
from matanui.exceptions import MataNuiStorerNotFoundException


def _check_filename(handle, filename=None):
    """
    Checks whether the file name of an object associated by OID matches
    that of the passed file name.
    
    @param handle: GridFS handle to resource.
    @param filename: Path/file name of the file (optional).
        
    @raise MataNuiStorerException: If the names do not match.
    """
    if filename is None or filename == '/':
        return
    
    try:
        handle_name = handle.name
    except AttributeError:
        handle_name = handle['filename']
    
    if handle_name != filename:
        message = ('File name mismatch for operation on object: %s vs. %s'
                   % (handle_name, filename))
        raise MataNuiStorerException(message)


class MongoGridFS(storerinterface.NullStorer):
    """Adapter to connect to a MongoDB GridFS storage subsystem."""
    EDITABLE_METADATA_ELEMENTS = ['filename',
                                  'owner',
                                  'contentType',
                                  'accessMode']
    REPLACABLE_METADATA_ELEMENTS = ['metadata']
    
    def __init__(self):
        storerinterface.NullStorer.__init__(self)
        self._db = None
        self._fs = None
        self._files_collection = None
        self._host = config.GRIDFS_HOST
        self._port = config.GRIDFS_PORT
        self._db_name = config.GRIDFS_DB_NAME
        self._gridfs_handle = None
        self._mongo_file_handle = None
        self._filename = None
        self._object_id = None


    @property
    def db(self):
        """Connection to the MongoDB instance."""
        if not self._db:
            self._db = pymongo.Connection(self._host)[self._db_name]
            if config.GRIDFS_USER:
                self._db.authenticate(config.GRIDFS_USER,
                                      config.GRIDFS_PASSWORD)
        return self._db
    
    
    @property
    def fs(self):
        """Connection to the GridFS."""
        if not self._fs:
            self._fs = gridfs.GridFS(self.db, config.GRIDFS_BUCKET)
        return self._fs
        
    
    @property
    def files_collection(self):
        """Connection to the DB "files" collection for GridFS."""
        if not self._files_collection:
            self._files_collection = self.db[config.GRIDFS_BUCKET].files
        return self._files_collection
    
    
    def get_content(self, filename=None, object_id=None):
        """
        Retrieves a file from the storage sub-system. The method requires a file
        name or an object ID to reference the resource.
        See L{matanui.storerinterface.NullStorer.get_content}.
        
        Note: The size of the returned data packages is aligned with the 
              configured chunk size in the GridFS.
        
        @param filename: Path/file name of the resource.
        @type filename: C{str}
        @param object_id: Object ID of the resource.
        @type object_id: C{str}
        
        @return: Content object.
        @rtype: L{matanui.storerinterface.ContentObject}
        """
        handle = self._get_gridfs(filename, object_id)
        return MongoContentObject(handle)


    def put_content(self, content_object, query_metadata=None):
        """
        Stores a file into the DB.
        See L{matanui.storerinterface.NullStorer.get_content}.
        
        @param content_object: Path/file name of the file to store.
        @type content_object: L{matanui.storerinterface.ContentObject}
        @param query_metadata: Meta-data to be stored, passed along with file
            content object.
        @type query_metadata: C{dict}
        
        @return: Storage backend's object ID.
        @rtype: C{str}
        """
        # Get old meta-data, if it exists.
        try:
            metadata = self._get_mongo_file_handle(content_object.filename)
            del metadata['_id']
        except MataNuiStorerException:
            metadata = {'filename': content_object.filename}
        
        if 'contentType' not in metadata:
            metadata['contentType'] = (content_object.content_type
                                       or mimetypes.guess_type(content_object.filename)[0])
        metadata['owner'] = content_object.owner
        
        # Mix in passed meta-data from query.
        metadata = self._mix_in_metadata(metadata, query_metadata)
        metadata = self._validate_access_mode(metadata)
        
        object_id = self.fs.put(content_object.data, **metadata)
        return str(object_id)


    def delete_file(self, filename=None, object_id=None):
        """
        Deletes a file (content and meta-data) from the file system in 
        the DB.
        See L{matanui.storerinterface.NullStorer.delete_file}.
        
        @param filename: Path/file name of the resource.
        @type filename: C{str}
        @param object_id: Object ID of the resource.
        @type object_id: C{str}
        
        @return: Storage backend's object ID of deleted file.
        @rtype: C{str}
        """
        try:
            deleted_id = self._get_gridfs(filename, object_id)._id
            self.fs.delete(deleted_id)
            self._object_id = None
            self._filename = None
            self._gridfs_handle = None
        except gridfs.errors.NoFile as err:
            raise MataNuiStorerException('Error deleting file: %s'
                                         % str(err))
        return str(deleted_id)


    def get_metadata(self, filename=None, object_id=None):
        """
        Retrieves the meta-data of a resource from the local file system in the
        DB.
        See L{matanui.storerinterface.NullStorer.get_metadata}.
        
        @param filename: Path/file name of the resource.
        @type filename: C{str}
        @param object_id: Object ID of the resource.
        @type object_id: C{str}
        
        @return: Object ID and meta-data object.
        @rtype: C{tupel} of C{str} and L{matanui.storerinterface.MetadataObject}
        """
        entry = self._get_mongo_file_handle(filename, object_id)
        return (str(entry['_id']), MongoMetadataObject(entry))


    def set_metadata(self, metadata, filename=None, object_id=None):
        """
        Sets the meta-data of a resource from the local file system in the
        DB.
        See L{matanui.storerinterface.NullStorer.set_metadata}.
        
        @param metadata: Meta-data to set on object.
        @type metadata: L{matanui.storerinterface.MetadataObject}
        @param filename: Path/file name of the resource.
        @type filename: C{str}
        @param object_id: Object ID of the resource.
        @type object_id: C{str}
        
        @return: Object ID of updated object.
        @rtype: C{str}
        """
        entry = self._get_mongo_file_handle(filename, object_id)
        new_metadata = self._mix_in_metadata(entry, metadata.content)
        new_metadata = self._validate_access_mode(new_metadata)
        self.files_collection.update({'_id': entry['_id']}, new_metadata)
        return str(entry['_id'])


    def list_resources(self, query):
        """ 
        Returns a list of resources in the style of a UN*X "ls" shell command
        satisfying the given query.
        See L{matanui.storerinterface.NullStorer.list_resources}.
        
        @param query: Search query, may contain command line wild cards ("*"
            and "?").
        @type query: C{str}
        
        @return: List of resources' listed with meta-data.
        @rtype: L{matanui.storerinterface.MetadataObject}
        
        @raise MataNuiStorerException: In case of errors from the storage
            sub-system.
        """
        re_query = storerinterface.shell_to_regex_query(query,
                                                        close_query=False)
        entries = self.files_collection.find({'filename': {'$regex': re_query}},
                                             sort=[('filename', pymongo.ASCENDING),
                                                   ('uploadDate', pymongo.ASCENDING)])
        newest_entries = {}
        for item in entries:
            newest_entries[item['filename']] = item
            
        unified_entries = storerinterface.filter_results(query,
                                                         newest_entries.keys())
        
        results = []
        for item in unified_entries:
            entry = newest_entries.get(item, {'filename': item,
                                              'conentType': 'collection'})
            # Remove potentially meta-data, as it may be excessively large.
            if 'metadata' in entry:
                del entry['metadata']
            results.append(entry)
        return MongoMetadataObject(results)


    def is_access_allowed(self, user, access_mode, filename=None, object_id=None,
                          dir_mode=False):
        """
        Checks whether the requested access mode for a user on a resource in the
        storage system is given.
        See L{matanui.storerinterface.NullStorer.is_access_allowed}.
        
        @param user: User name.
        @type user: C{str}
        @param access_mode: UN*X style access mode indicator.
        @type access_mode: C{int}
        @param filename: Path/file name of the file.
        @type filename: C{str}
        @param object_id: Object ID of the resource.
        @type object_id: C{str}
        @param target: Path/file name of the target of an operation.
        @type target: C{str}
        @param dir_mode: Are we interested in directory level access, e. g. for
            writing a file into the directory or listing it.
        @type dir_mode: C{bool}
        
        @return: C{True} if the desired access is allowed.
        @rtype: C{bool}
        
        @raise matanui.exceptions.MataNuiStorerException: In case of a
            file name mismatch. 
        """
        if filename is None and object_id is None:
            return False
    
        try:
            entry = self._get_mongo_file_handle(filename, object_id)
        except MataNuiStorerNotFoundException:
            if dir_mode:
                # Now bark up the FS tree.
                segments = filename.split('/')[1:-1]
                parent_paths = ['/' + '/'.join(segments[:i])
                                for i in range(len(segments), -1, -1)]
                entry = None
                for path in parent_paths:
                    try:
                        entry = self._get_mongo_file_handle(path, object_id)
                        # Found closest parent: Stop ... Hammer Time!
                        break
                    except MataNuiStorerNotFoundException:
                        # Create a dummy one with defaults
                        # (user does not own, for safety).
                        entry = {'filename': path,
                                 'accessMode': config.DEFAULT_PERMISSIONS,
                                 'contentType': 'collection',
                                 'owner': None}
            else:
                return False
        
        file_access_mode = entry.get('accessMode', None)
        owner = entry.get('owner', None)
        
        if file_access_mode is None:
            file_access_mode = config.DEFAULT_PERMISSIONS
    
        if user == owner:
            compare_mode = (file_access_mode >> storerinterface.OWNER_SHIFT) & access_mode
        else:
            compare_mode = file_access_mode & access_mode
        
        result = (compare_mode == access_mode)
        return result
        

    def exists(self, path):
        """
        Checks, whether an entry with the given path exists. In case of
        directories without an explicit entry, it will be checked whether
        any entries containing this path as a base exist.
        See L{matanui.storerinterface.NullStorer.exists}.
        
        @param path: Path of the resource to check.
        @type path: C{str}
        
        @return: True if it exists.
        @rtype: C{bool}
        """
        try:
            entry = self._get_mongo_file_handle(path)
            if entry: 
                return True
        except MataNuiStorerException:
            result = False
            unique_entries = self._entries_starting_with(path)
            path_base = path
            if not path_base.endswith('/'):
                path_base = '%s/' % path
            for item in unique_entries:
                if item == path or item.startswith(path_base):
                    result = True
                    break
            return result


    def is_file(self, filename=None, object_id=None):
        """
        Checks whether the resource indicated is a file.
        See L{matanui.storerinterface.NullStorer.is_file}.
        
        @param filename: Path/file name of the resource.
        @type filename: C{str}
        @param object_id: Object ID of the resource.
        @type object_id: C{str}
        
        @return: C{True} if the resource is a file.
        @rtype: C{bool}
        
        @raise matanui.exceptions.MataNuiStorerException: In case of a
            name mismatch. 
        """
        # This implementation may be a bit ugly, but it works (hopefully).
        result = False
        try:
            entry = self._get_mongo_file_handle(filename, object_id)
            if entry.get('contentType', '') == 'collection': 
                result = False
            else:
                result = True
        except MataNuiStorerNotFoundException:
            if self.exists(filename):
                result = False
            else:
                result = True
        return result


    def is_directory(self, filename=None, object_id=None):
        """
        Checks whether the resource indicated is a directory.
        See L{matanui.storerinterface.NullStorer.is_directory}.
        
        @param filename: Path/file name of the resource.
        @type filename: C{str}
        @param object_id: Object ID of the resource.
        @type object_id: C{str}
        
        @return: C{True} if the resource is a directory.
        @rtype: C{bool}
        
        @raise matanui.exceptions.MataNuiStorerException: In case of a
            name mismatch. 
        """
        return not self.is_file(filename, object_id)


    def _get_gridfs(self, filename=None, object_id=None):
        """
        Accessor to GridFS handle of object. The method requires a file name or an object ID
        to perform the check. In case of both given, it verifies whether the
        file name matches that of the object referenced by the ID. If not,
        an exception is raised.
        
        @param filename: Path/file name of the file.
        @type filename: C{str}
        @param object_id: Object ID of the resource.
        @type object_id: C{str}
        
        @return: MongoDB GridFS file handle.
        @rtype: L{gridfs.grid_file.GridOut}
        """
        if object_id:
            handle = self._get_gridfs_by_oid(object_id)
            if filename and filename != '/':
                _check_filename(handle, filename)
        else:
            handle = self._get_gridfs_by_name(filename)
        return handle
    

    def _get_mongo_file_handle(self, filename=None, object_id=None):
        """
        Accessor to MongoDB files collection handle. The method requires a file name or an object ID
        to perform the check. In case of both given, it verifies whether the
        file name matches that of the object referenced by the ID. If not,
        an exception is raised.
        
        @param filename: Path/file name of the file.
        @type filename: C{str}
        @param object_id: Object ID of the resource.
        @type object_id: C{str}
        
        @return: MongoDB file collection document.
        @rtype: L{dict}
        """
        if object_id:
            handle = self._get_mongo_file_handle_by_oid(object_id)
            if filename and filename != '/':
                _check_filename(handle, filename)
        else:
            handle = self._get_mongo_file_handle_by_name(filename)
        return handle
    

    def _get_gridfs_by_name(self, filename):
        """Caching accessor of GridFS handle."""
        if filename != self._filename or not self._gridfs_handle:
            self._filename = filename
            try:
                self._gridfs_handle = self.fs.get_last_version(filename)
            except gridfs.errors.NoFile as err:
                raise MataNuiStorerNotFoundException("Did not find resource with name %s: %s"
                                                     % (filename, str(err)))
            self._object_id = self._gridfs_handle._id
        return self._gridfs_handle

    
    def _get_gridfs_by_oid(self, object_id):
        """Caching accessor of GridFS handle."""
        if isinstance(object_id, str):
            object_id = bson.ObjectId(object_id)
        
        if object_id != self._object_id or not self._gridfs_handle:
            self._object_id = object_id
            try:
                self._gridfs_handle = self.fs.get(object_id)
            except gridfs.errors.NoFile as err:
                raise MataNuiStorerNotFoundException("Did not find resource with object ID %s: %s"
                                                     % (object_id, str(err)))
            self._filename = self._gridfs_handle.name
        return self._gridfs_handle


    def _get_mongo_file_handle_by_name(self, filename):
        """Caching accessor of MongoDB files collection handle."""
        if filename != self._filename or not self._mongo_file_handle:
            entries = self.files_collection.find({'filename': filename},
                                                 sort=[('uploadDate',
                                                        pymongo.DESCENDING)])
            try:
                entry = entries[0]
            except IndexError:
                raise MataNuiStorerNotFoundException("Did not find object with name %s"
                                                     % filename)
            self._mongo_file_handle = entry
            self._filename = self._mongo_file_handle['filename']
            self._object_id = self._mongo_file_handle['_id']
        return self._mongo_file_handle


    def _get_mongo_file_handle_by_oid(self, object_id):
        """Caching accessor of GridFS handle."""
        if isinstance(object_id, str):
            object_id = bson.ObjectId(object_id)
        
        if object_id != self._object_id or not self._mongo_file_handle:
            self._object_id = object_id
            self._mongo_file_handle = self.files_collection.find_one({'_id':
                                                                      object_id})
            if not self._mongo_file_handle:
                raise MataNuiStorerNotFoundException("Did not find object with ID %s"
                                                     % object_id)
            self._filename = self._mongo_file_handle['filename']
        return self._mongo_file_handle


    def _scrub_metadata(self, metadata):
        """
        "Scrubs" the meta-data passed in and returns meta-data suitable for the
        update. The meta-data returned consists of two dictionaries, the first
        one is for updating the core/system meta-data, and the second one is
        for setting a completely new "metadata" element with custom meta-data.
        
        @param metadata: Meta-data to clean.
        @param metadata: C{dict}
        
        @return: Updater and replacer meta-data.
        @rtype: C{tupel}: (C{dict}, C{dict})
        """
        if metadata is None:
            metadata = {}
        updater = {}
        replacer = {}
        
        for item in self.EDITABLE_METADATA_ELEMENTS:
            if item in metadata:
                updater[item] = metadata[item]
        
        for item in self.REPLACABLE_METADATA_ELEMENTS:
            if item in metadata:
                replacer[item] = metadata[item]
        return updater, replacer
        
    
    def _mix_in_metadata(self, old, new):
        """Helps to merge new meta-data into old one."""
        updater, replacer = self._scrub_metadata(new)
        result = old.copy()
        if not updater and not replacer:
            # Short cut if we're left empty, so we won't overwrite stuff.
            return result
        for item in replacer:
            result[item] = replacer[item]
        result.update(updater)
        return result


    def _validate_access_mode(self, metadata, umask=None, default_permissions=None):
        """Validated (checks and fixes) the access mode in a meta-data dict."""
        if umask is None:
            umask = config.UMASK
        if default_permissions is None:
            default_permissions = config.DEFAULT_PERMISSIONS
        access_mode = metadata.get('accessMode', default_permissions)
        access_mode = ((access_mode & storerinterface.PRIV_MAX)
                       & (umask ^ storerinterface.PRIV_MASK))
        metadata['accessMode'] = access_mode
        return metadata
        
    
    def _entries_starting_with(self, path):
        """
        Returns a list of all (unique) entries starting with a given path.
        
        @param path: Path to search for.
        @type path: C{str}
        
        @return: (Unique) entries' names.
        @rtype: C{list} of C{str}
        """
        re_query = '^%s' % path
        entries = self.files_collection.find({'filename': {'$regex': re_query}})
        if entries.count() == 0:
            return []

        # "Uniquify" entries (only one entry per path), and no deeper than
        # one level below current collection path.
        unique_entries = set()
        for item in entries:
            unique_entries.add(item['filename'])
        return list(unique_entries)



class MongoContentObject(storerinterface.ContentObject):
    """MongoDB/GridFS specific version of the L{ContentObject}."""
    
    def __init__(self, file_handle):
        """
        Constructor.
        
        @param file_handle: GridFS file handle.
        @type file_handle: 
        """
        storerinterface.ContentObject.__init__(self)
        self.data = file_handle
        
        # Make it file-like.
        self.data.close = _dummy_close

        self.checksum = str(self.data.md5)
        self.content_type = str((self.data.content_type
                                 or mimetypes.guess_type(self.data.filename)[0]))
        
    @property
    def length(self):
        """See L{ContentObject.length}."""
        return self.data.length
    
    @property
    def block_size(self):
        """See L{ContentObject.block_size}."""
        return self.data.chunk_size
    
    @property
    def last_modified(self):
        """See L{ContentObject.last_modified}."""
        return self.data.upload_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    @property
    def filename(self):
        """See L{ContentObject.filename}."""
        return str(self.data.filename)
    
    @property
    def object_id(self):
        """See L{ContentObject.object_id}."""
        return str(self.data._id) # pylint: disable=W0212
    


class MongoMetadataObject(storerinterface.MetadataObject):
    """MongoDB/GridFS specific version of the L{MetadataObject}."""
    def _default(self, obj):
        return json_util.default(obj)
    
    def _object_hook(self, dct):
        return json_util.object_hook(dct)



def _dummy_close(self): # pylint: disable=W0613
    """Intentionally left blank for dummy."""
