import shutil
import datetime
import os
import uuid

from pyf.services.model import DBSession
from pyf.services.model import EventStorage as StorageTable
from pylons import config

def get_storage(section="misc"):
    storage_folder = None
    if 'storage_dir' in config['global_conf']:
        storage_folder = config['global_conf']['storage_dir']
    else:
        storage_folder = config['storage_dir']
        
    return Storage(os.path.join(storage_folder, section))

class Storage(object):
    """Storage may store some files on the filesystem with a specific
    tree definition.
    For example : basedir/YY/MM/DD
    """

    def __init__(self, basedir, tree_arborescence_definition='%Y/%m/%d'):
        """Initialized a storage with basedir
        """
        self.basedir = basedir
        self.tree_arborescence_definition = tree_arborescence_definition

    def store(self, source_file):
        """Store the open file on the storage
        The store method return the uuid of the new file
        """
        uuid_filename = uuid.uuid4().get_hex()
        abs_dirname, dirname = self.__init_tree_arborescence()
        target_path = os.path.join(abs_dirname, uuid_filename)
        target_file = open(target_path, 'wb')
        source_file.seek(0)
        shutil.copyfileobj(source_file, target_file)
        source_file.seek(0)
        target_file.close()

        storage = StorageTable()
        storage.uuid = uuid_filename
        storage.dirname = dirname

        DBSession.add(storage)
        DBSession.flush()

        return uuid_filename

    def get_filename(self, uuid_filename):
        """Return the filename related to the uuid_filename
        """
        storage = StorageTable.by_uuid(uuid_filename)
        dirname = storage.dirname
        abs_filename = os.path.join(self.basedir, dirname, uuid_filename)
        return abs_filename

    def get_file(self, uuid_filename):
        """Return an open file related to the uuid_filename
        """
        abs_filename = self.get_filename(uuid_filename)
        if not os.path.exists(abs_filename):
            raise IOError('File %s does not exist' % abs_filename)

        return open(abs_filename, 'rb')

    def __init_tree_arborescence(self):
        """Initialize the tree arborescence directory
        """
        if not os.path.exists(self.basedir):
            os.makedirs(self.basedir)

        dirname = ''
        now = datetime.datetime.now()
        for dir_def in self.tree_arborescence_definition.split('/'):
            dirname = os.path.join(dirname,
                    datetime.datetime.strftime(now, dir_def))

        abs_dirname = os.path.join(self.basedir, dirname)

        if not os.path.exists(abs_dirname):
            os.makedirs(abs_dirname)

        return abs_dirname, dirname

