import os
import sys
import threading

from pathtools import path
from watchdog.utils import has_attribute, DaemonThread
from watchdog.utils.dirsnapshot import DirectorySnapshotDiff 

def _thread_init(self):
    threading.Thread.__init__(self)
    if has_attribute(self, 'daemon'):
        self.daemon = True
    else:
        self.setDaemon(True)
    self._stopped_event = threading.Event()

    # this line is wrong originally
    if not has_attribute(self._stopped_event, 'is_set'):
        self._stopped_event.is_set = self._stopped_event.isSet

def _dir_diff_init(self, ref_dirsnap, dirsnap):
    import stat
    self._files_deleted = list()
    self._files_modified = list()
    self._files_created = list()
    self._files_moved = list()

    self._dirs_modified = list()
    self._dirs_moved = list()
    self._dirs_deleted = list()
    self._dirs_created = list()

    # Detect all the modifications.
    for path, stat_info in dirsnap.stat_snapshot.items():
        if path in ref_dirsnap.stat_snapshot:
            ref_stat_info = ref_dirsnap.stat_info(path)
            # XXX
            if stat_info.st_mtime != ref_stat_info.st_mtime:
                if stat.S_ISDIR(stat_info.st_mode):
                    self._dirs_modified.append(path)
                else:
                    self._files_modified.append(path)

    paths_deleted = ref_dirsnap.paths - dirsnap.paths
    paths_created = dirsnap.paths - ref_dirsnap.paths

    # Detect all the moves/renames.
    # Doesn't work on Windows, so exlude on Windows.
    if not sys.platform.startswith('win'):
        for created_path in paths_created.copy():
            created_stat_info = dirsnap.stat_info(created_path)
            for deleted_path in paths_deleted.copy():
                deleted_stat_info = ref_dirsnap.stat_info(deleted_path)
                if created_stat_info.st_ino == deleted_stat_info.st_ino:
                    paths_deleted.remove(deleted_path)
                    paths_created.remove(created_path)
                    if stat.S_ISDIR(created_stat_info.st_mode):
                        self._dirs_moved.append((deleted_path, created_path))
                    else:
                        self._files_moved.append((deleted_path, created_path))

    # Now that we have renames out of the way, enlist the deleted and
    # created files/directories.
    for path in paths_deleted:
        stat_info = ref_dirsnap.stat_info(path)
        if stat.S_ISDIR(stat_info.st_mode):
            self._dirs_deleted.append(path)
        else:
            self._files_deleted.append(path)

    for path in paths_created:
        stat_info = dirsnap.stat_info(path)
        if stat.S_ISDIR(stat_info.st_mode):
            self._dirs_created.append(path)
        else:
            self._files_created.append(path)
            
def _get_dir_walker(recursive, topdown=True, followlinks=False):
    from functools import partial
    if recursive:
        walk = partial(os.walk, topdown=topdown)
    else:
        def walk(path, topdown=topdown):
            try:
                yield next(os.walk(path, topdown))
            except NameError:
                yield os.walk(path, topdown).next() #IGNORE:E1101
    return walk

def monkey_patch():
    """Watchdog has a bug in Python2.5, reference to
    
    https://github.com/gorakhargosh/watchdog/issues#issue/34
    
    Here we patch the bug
    
    """
            
    DaemonThread.__init__ = _thread_init
    
    DirectorySnapshotDiff.__init = _dir_diff_init
    
    # os.walk in python2.5 doesn't support followlinks parameter
    if sys.version_info[:2] == (2, 5):
        path.get_dir_walker = _get_dir_walker
        
        