
import os
import utils
import shutil
import uuid
import datetime

class FileObjectIterator(object):
    """iterator to be used in the ``all`` property which returns all files in the
    filestorage"""
    
    def __init__(self, fs):
        self.fs = fs
        self.iterator = os.walk(fs.root_path, topdown=True)
        self.filenames = [] # list of filenames to consume
        
    def next(self):
        """return the next file pointer"""
        if len(self.filenames)==0:
            while True:
                # this might raise StopIteration but we simply pass it on
                folder, dirs, filenames = self.iterator.next()
                if len(filenames)>0:
                    break
            # a new list of filenames to use
            self.filenames = [os.path.join(folder,f) for f in filenames]
        filename = self.filenames.pop(0)
        
        # cut off the root path
        filename = filename[len(self.fs.root_path)+1:] # also remove the leading /
        return filename, self.fs[filename]
    

class FilesystemStore(object):
    """store files on the filesystem"""
    
    def __init__(self, root_path, template="/%Y/%m"):
        """initialize the filesystem storage with a folder ``root_path`` 
        in which the files will be stores and a ``template`` for naming the file"""
        
        self.root_path = root_path
        if template.startswith("/"):
            template=template[1:]
        self.template = template
        
    def add(self, file, filename=None):
        """store a file"""
        if filename is None:
            filename = unicode(uuid.uuid4())
            
        filepath = self.filepath # the directory path relative to the root
        fullpath = os.path.join(self.root_path, filepath) # absolute path to directory
        filename = utils.string2filename(filename, fullpath) # compute a filename
        
        subfilepath = os.path.join(filepath, filename) # full path without root path
        self._save(subfilepath, file)
        return subfilepath
        
    def _save(self, filename, file):
        """actually save the file"""

        full_filename = os.path.join(self.root_path, filename) # full path to file
        path = os.path.split(full_filename)[0] # directory path
            
        if not os.path.exists(path):
            os.makedirs(path) # make sure the path exists
        
        # TODO: What should happen if file now exists e.g. in case of concurrency?
        # Do we need locking or do we need some way to report it? Probably the latter
        fp = open(full_filename, "wb")

        while True:
            chunk = file.read(8192)
            if not chunk:
                break
            fp.write(chunk)
        fp.close()        

    def get_fs_filename(self, filename):
        """return the full filename with filesystem path of the given asset filename.
        It basically means joining the base path and the filename"""
        return os.path.join(self.root_path, filename)
    
    def get(self, filename):
        """return the file with the given filename as a file pointer"""
        full_filename = os.path.join(self.root_path, filename)
        if not os.path.isfile(full_filename):
            raise KeyError(filename)
        return open(full_filename,"rb")
    
    __getitem__ = get

    def delete(self, filename):
        """delete the file identified by ``filename``"""
        full_filename = os.path.join(self.root_path, filename)
        if os.path.isfile(full_filename):
            os.remove(full_filename)
            
    def update(self, file, filename):
        """update the file in place"""
        self._save(filename, file)        
         
    def sizeof(self, filename):
        """get size of specified file"""
        full_filename = os.path.join(self.root_path, filename)
        f = open(full_filename)
        size = os.fstat(f.fileno())[6]
        f.close()
        return size

    def copy(self, source, dest=None):
        """copy a file from source to destination"""
        if dest is None:
            dest = unicode(uuid.uuid4())
            
        filepath = self.filepath # the directory path relative to the root
        fullpath = os.path.join(self.root_path, filepath) # absolute path to directory
        dest = utils.string2filename(dest, fullpath) # compute a filename

        dest_filename = os.path.join(self.root_path, filepath, dest) # full path to file
        source_filename = os.path.join(self.root_path, source)
        path = os.path.split(dest_filename)[0] # directory path
        print dest_filename, source_filename
            
        if not os.path.exists(path):
            os.makedirs(path) # make sure the path exists
        shutil.copyfile(source_filename, dest_filename)
        return os.path.join(filepath, dest)


    @property
    def filepath(self):
        """the path between root_path and filename"""
        return datetime.datetime.now().strftime(self.template)
        
    def __iter__(self):
        """return an iterator over ourself"""
        return FileObjectIterator(self)
        
        
        
