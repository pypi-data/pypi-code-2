from os import walk, stat
from os.path import isdir, join
import UserDict


class Snapshot(UserDict.IterableUserDict):
    def __init__(self, ignore=[]):
        UserDict.IterableUserDict.__init__(self)

        assert not type(ignore) in (basestring,)
        self.ignore = ignore

    def __eq__(self, compared_with):
        if not isinstance(compared_with, Snapshot):
            return False

        if not len(self) is len(compared_with):
            return False

        for item in self:
            if [i for i in self.ignore if i in item]:
                # This item is being ignored
                continue
            if item not in compared_with:
                return False
            if not self[item] == compared_with[item]:
                return False

        return True


class Monitor(object):
    """
    Looks at a directory and tells you if anything has changed within it
    """
    def __init__(self, directory, ignore_directory=[]):
        if not isdir(directory):
            raise IOError('%s is not a directory, cannot monitor it for '
                'changes' % directory)

        self.directory = directory
        self.snapshot = None
        self.ignore_directory = ignore_directory

    def has_changed(self):
        older_snapshot = self.snapshot

        self.snapshot = Snapshot(ignore=self.ignore_directory)

        for (dirpath, dirnames, filenames) in walk(self.directory):
            for basename in filenames:
                filename = join(dirpath, basename)
                lastmod = stat(filename).st_mtime
                self.snapshot[filename] = lastmod

        if older_snapshot == self.snapshot or older_snapshot is None:
            return False

        return True
