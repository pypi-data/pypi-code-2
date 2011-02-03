# -*- coding: utf-8 -*-
'''Interfaces to storer back-ends.'''
# pylint: disable=W0613,R0201,W0105

## Created: 2010-09-11 Guy K. Kloss <Guy.Kloss@aut.ac.nz>
## 
## Copyright 2010 Guy K. Kloss
## Some rights reserved.
##
## http://www.aut.ac.nz/

__author__ = 'Guy K. Kloss <Guy.Kloss@aut.ac.nz>'

import re
import json

from matanui import config

# Some UN*X like privileges for storage system operations.
PRIV_READ = 04
PRIV_WRITE = 02
PRIV_READ_WRITE = PRIV_READ | PRIV_WRITE
WORLD_MASK = PRIV_READ_WRITE
GROUP_SHIFT = 3
GROUP_MASK = WORLD_MASK << GROUP_SHIFT
OWNER_SHIFT = 6
OWNER_MASK = WORLD_MASK << OWNER_SHIFT
PRIV_MAX = 0666
PRIV_MASK = 0777


class NullStorer(object):
    """
    Null pattern/default implementation of the data-related interface.
    """

    def __init__(self):
        """Constructor."""


    def get_content(self, filename=None, object_id=None):
        """ 
        Retrieves a file from the storage sub-system. The method requires a file
        name or an object ID to reference the resource.
        
        @param filename: Path/file name of the resource.
        @type filename: C{str}
        @param object_id: Object ID of the resource.
        @type object_id: C{str}
        
        @return: A content object.
        @rtype: L{ContentObject}
        
        @raise MataNuiStorerException: In case of errors from the storage
            sub-system.
        """
        return None
    

    def put_content(self, content_object, query_metadata=None):
        """ 
        Stores a file in the storage sub-system.
        
        @param content_object: Content object for the file to put.
        @type content_object: L{matanui.storerinterface.ContentObject}
        @param query_metadata: Meta-data to be stored, passed along with file
            content object.
        @type query_metadata: C{dict}
        
        @return: Unique object ID of storage system.
        @rtype: C{str}
        
        @raise MataNuiStorerException: In case of errors from the storage
            sub-system.
        """
        return None


    def delete_file(self, filename=None, object_id=None):
        """ 
        Deletes a file from the storage sub-system. The method requires a file
        name or an object ID to reference the resource.
        
        @param filename: Path/file name of the resource.
        @type filename: C{str}
        @param object_id: Object ID of the resource.
        @type object_id: C{str}
        
        @return: Object ID of the deleted file.
        @rtype: C{str}
        
        @raise MataNuiStorerException: In case of errors from the storage
            sub-system.
        """
        return None
    

    def get_metadata(self, filename=None, object_id=None):
        """ 
        Retrieves a resource's meta-data from the storage sub-system. The method
        requires a file name or an object ID to reference the resource.
        
        @param filename: Path/file name of the resource.
        @type filename: C{str}
        @param object_id: Object ID of the resource.
        @type object_id: C{str}
        
        @return: Object ID and meta-data object.
        @rtype: C{tupel} of C{str} and L{MetadataObject}
        
        @raise MataNuiStorerException: In case of errors from the storage
            sub-system.
        """
        return None
    

    def set_metadata(self, metadata, filename=None, object_id=None):
        """ 
        Sets a resource's meta-data from the storage sub-system. The method 
        requires a file name or an object ID to reference the resource.
        
        @param metadata: A meta-data object.
        @type metadata: L{MetadataObject}
        @param filename: Path/file name of the resource.
        @type filename: C{str}
        @param object_id: Object ID of the resource.
        @type object_id: C{str}
        
        @return: Object ID of updated resource.
        @rtype: C{str}
        
        @raise MataNuiStorerException: In case of errors from the storage
            sub-system.
        """
        return None
    

    def list_resources(self, query):
        """ 
        Returns a list of resources in the style of a UN*X "ls" shell command
        satisfying the given query.
        
        @param query: Search query, may contain command line wild cards ("*"
            and "?").
        @type query: C{str}
        
        @return: List of resources' listed with meta-data.
        @rtype: L{matanui.storerinterface.MetadataObject}
        
        @raise MataNuiStorerException: In case of errors from the storage
            sub-system.
        """
        return None


    def is_access_allowed(self, user, access_mode, filename=None, object_id=None,
                          dir_mode=False):
        """
        Checks whether the requested access mode for a user on a resource in the
        storage system is given. The method requires a file name or an object ID
        to perform the check.
        
        @param user: User name.
        @type user: C{str}
        @param access_mode: UN*X style access mode indicator.
        @type access_mode: C{int}
        @param filename: Path/file name of the file.
        @type filename: C{str}
        @param object_id: Object ID of the resource.
        @type object_id: C{str}
        @param dir_mode: Are we interested in directory level access, e. g. for
            writing a file into the directory or listing it.
        @type dir_mode: C{bool}
        
        @return: C{True} if the desired access is allowed.
        @rtype: C{bool}
        
        @raise @raise matanui.exceptions.MataNuiStorerException: In case of a
            file name mismatch. 
        """
        return False


    def is_file(self, filename=None, object_id=None):
        """
        Checks whether the resource indicated is a file.
        
        @param filename: Path/file name of the resource.
        @type filename: C{str}
        @param object_id: Object ID of the resource.
        @type object_id: C{str}
        
        @return: C{True} if the resource is a file.
        @rtype: C{bool}
        
        @raise @raise matanui.exceptions.MataNuiStorerException: In case of a
            name mismatch. 
        """
        return False


    def is_directory(self, filename=None, object_id=None):
        """
        Checks whether the resource indicated is a directory.
        
        @param filename: Path/file name of the resource.
        @type filename: C{str}
        @param object_id: Object ID of the resource.
        @type object_id: C{str}
        
        @return: C{True} if the resource is a directory.
        @rtype: C{bool}
        
        @raise @raise matanui.exceptions.MataNuiStorerException: In case of a
            name mismatch. 
        """
        return False


    def exists(self, path):
        """
        Checks, whether an entry with the given path exists.
        
        @param path: Path of the resource to check.
        @type path: C{str}
        
        @return: True if it exists.
        @rtype: C{bool}
        """
        return False



class ContentObject(object): # pylint: disable=R0903
    """
    Interface for passing file/content information back from the storage to
    the service layer.
    """
    
    data = None
    """File-like data object."""
    
    block_size = 8192
    """Block size for reading (C{int})."""
    
    length = 0
    """Length of conent in bytes (C{int})."""
    
    checksum = ''
    """Checksum of data object (MD5) (C{str})."""
    
    content_type = ''
    """MIME type of data object (C{str})."""
    
    last_modified = ''
    """Last upload/modification date (C{str})."""
    
    filename = ''
    """Assigned (file) name of the resource (C{str})."""
    
    object_id = ''
    """Unique object ID of storage system (C{str})."""

    metadata = None
    """Additional meta-data associated with the object (L{MetadataObject})."""
    
    owner = None
    """Owner of the file (user name or DN of the X.509 cert.) (C{str})."""

    access_mode = config.DEFAULT_PERMISSIONS
    """UN*X style access mode definition, default: 0644 (C{int})."""



class MetadataObject(object):
    """
    Interface for passing meta-data information back from the storage to
    the service layer.
    """
    
    content = None
    """The content to be stored/serialised, commonly  a C{dict}."""
    
    # The following are (de-)serialisation hook functions used in the
    # conversion to/from JSON.
    _default = None
    _object_hook = None
    
    
    def __init__(self, content=None):
        """
        Constructor.
        
        @param content: Content to initialise object with.
        """
        self.content = content
    
    
    @property
    def json_string(self):
        """Content representation in a JSON C{str}."""
        return json.dumps(self.content, default=self._default)
    
    @json_string.setter
    def json_string(self, a_string):
        self.content = json.loads(a_string, object_hook=self._object_hook)
    
    
    def get_json_stream(self, fp):
        """
        Serialisation of the content into a file-like object.
        
        @param fp: File like object (supporting the C{.write()} method(s).
        """
        return json.dump(self.content, fp, default=self._default)

        
    def set_from_json_stream(self, fp):
        """
        Deserialisation of a file-like object into the content.
        
        @param fp: File like object (supporting the C{.read()} method(s).
        """
        self.content = json.load(fp, object_hook=self._object_hook)

        


#    @property
#    def is_link(self):
#        """
#        Determines whether the associated item is a symbolic link or not.
#        If it is a link the link target can be retrieved using the C{getChildren} method.
#        """


## TODO: Take this out. This is just for reference on how DF does it.
#class _NullDataStorer(object):
#    """
#    Null pattern/default implementation of the data-related interface.
#
#    datafinder.persistence.data.datastorer.NullDataStorer
#    """
#
#    @property
#    def link_target(self):
#        """ 
#        Getter for the logical identifier of the item the link is pointing to or C{None}.
#        
#        @return: Link target identifier.
#        @rtype: C{unicode} or C{None}
#        """
#        return None
#    
#    @property
#    def is_link(self):
#        """
#        Determines whether the associated item is a symbolic link or not.
#        If it is a link the link target can be retrieved using the C{getChildren} method.
#        
#        @return: Flag indicating whether it is a link or not.
#        @rtype: C{bool}
#        """
#        return False
#    
#    @property
#    def is_collection(self):
#        """
#        Determines whether the associated item is an item container or not.
#        
#        @return: Flag indicating whether it is an item container or not.
#        @rtype: C{bool}
#        """
#        return False
#    
#    @property
#    def is_leaf(self):
#        """
#        Determines whether the associated item is a leaf node or not.
#        
#        @return: Flag indicating whether it is a leaf node or not.
#        @rtype: C{bool}
#        """
#        return False
#
#    @property
#    def can_add_children(self):
#        """
#        Determines whether it is possible to add new items below this item.
#        
#        @return: Flag indicating the possibility of adding new items below.
#        @rtype: C{bool}
#        """
#        return False
#    
#    def create_collection(self, recursively):
#        """ 
#        Creates a collection.
#        
#        @param recursively: If set to C{True} all missing collections are created as well.
#        @type recursively: C{bool}
#        """
#        
#    def create_resource(self):
#        """ 
#        Creates a resource. 
#        """
#    
#    def create_link(self, destination):
#        """ 
#        Creates a symbolic link to the specified destination.
#        
#        @param destination: Identifies the item that the link is pointing to.
#        @type destination: C{object} implementing the C{NullDataStorer} interface.
#        """
#    
#    def get_children(self):
#        """ 
#        Retrieves the logical identifiers of the child items. 
#        In case of a symbolic link the identifier of the link target is returned.
#        
#        @return: List of the child item identifiers.
#        @rtype: C{list} of C{unicode} 
#        """
#        
#    def exists(self):
#        """ 
#        Checks whether the item does already exist.
#        
#        @return: Flag indicating the existence of the item.
#        @rtype: C{bool}
#        """
#        
#    def delete(self):
#        """ 
#        Deletes the item. 
#        """
#        
#    def copy(self, destination):
#        """ 
#        Copies the associated item.
#        
#        @param destination: Identifies the copy of the item.
#        @type destination: C{object} implementing the C{NullDataStorer} interface. 
#        """
#        
#    def move(self, destination):
#        """ 
#        Moves the associated item.
#        
#        @param destination: Identifies the moved item.
#        @type destination: C{object} implementing the C{NullDataStorer} interface. 
#        """
#        
#    def read_data(self):
#        """ 
#        Returns the associated data.
#        
#        @return: Associated data.
#        @rtype: C{object} implementing the file protocol.
#        """
#        
#        return StringIO("")
#    
#    def write_data(self, data):
#        """ 
#        Writes data of the associated item.
#        
#        @param data: Associated data.
#        @type data: C{object} implementing the file protocol.
#        """
#
#
## TODO: Take this out. This is just for reference on how DF does it.
#class _NullMetadataStorer(object):
#    """ 
#    Null pattern / default implementation of the meta-data-related interface.
#    
#    datafinder.persistence.metadata.metadatastorer.NullMetadataStorer
#    """
#    
#    def retrieve(self, propertyIds=None):
#        """ 
#        Retrieves all meta data associated with the item.
#        C{propertyIds} allows explicit selection of meta data.
#        
#        @return: Meta data of the associated item.
#        @rtype: C{dict} of C{unicode},
#            L{MetadataValue<datafinder.common.metadata.value_mapping.MetaddataValue>}
#        """
#
#    def update(self, properties):
#        """ 
#        Update the associated meta data. 
#        Adds new properties or updates existing property values. 
#        
#        @param properties: New / updated meta data.
#        @type properties: C{dict} of C{unicode}, C{object}
#        """
#    
#    def delete(self, propertyIds):
#        """
#        Deletes the selected meta data.
#        
#        @param propertyIds: Specifies the meta data that has to be deleted.
#        @type propertyIds: C{list} of C{unicode} 
#        """
#    
#    def search(self, restrictions):
#        """ 
#        Allows searching for items based on meta data restrictions.
#        
#        @param restrictions: Boolean conjunction of meta data restrictions.
#                             For defined search operators see L{datafinder.persistence.constants}.
#        @type restrictions: C{list}
#        
#        @return: List of matched item identifiers.
#        @rtype: C{list} of C{unicode}
#        """



def filter_results(query, entries):
    """
    Filters all entries, and only returns the ones matching the query.
    
    @param query: Search query, may contain command line wild cards ("*"
        and "?").
    @type query: C{str}
    
    @return: List of resources remaining.
    @rtype: C{list} of C{str}
    """
    # Keep only those, that start with the query path base (up to first slash).
    query_base = query.rsplit('/', 1)[0]
    index = len(query_base) + 1
    left_path_reduced = [item for item in entries
                         if item.startswith(query[:index])]
    
    # Reduce the list down to those entries only that are directly underneath
    # the base path.
    path_reduced = list(set(['/'.join([query_base, item[index:].split('/', 1)[0]])
                             for item in left_path_reduced
                             if item[index:].split('/', 1)[0]]))

    re_query = shell_to_regex_query(query)
    
    # Apply the regex filter.
    result = [item for item in path_reduced
                  if re.search(re_query, item)]
    
    return result


def shell_to_regex_query(query, close_query=True):
    """
    Convert a UN*X compatible shell query to a regex query.
    
    @param query: Shell like query string (as e. g. used for "ls" command).
    @type query: C{str}
    @param close_query: Shall the query be "closed" (finished with a "$" at the
        end), if appropriate for the query string? (default: True).
    @type close_query: C{bool}
    
    @return: Regular expression query.
    @rtype: C{str}
    """
    # Make a regular expression query out of the "shell like" query.
    re_query = '^%s' % query 
    # Protect ".":
    re_query = re_query.replace('.', '\.')
    # Replace "?":
    re_query = re_query.replace('?', '.')
    # Replace "*" (use a non-greedy expression):
    re_query = re_query.replace('*', '.*?')
    
    # If we don't have an "open query", close it with the line end indicator "$".
    if close_query and not (re_query.endswith('/') or re_query.endswith('*')):
        re_query = '%s$' % re_query
    return re_query
