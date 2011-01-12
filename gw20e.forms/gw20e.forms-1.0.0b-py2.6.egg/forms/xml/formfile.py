import os
import sys


class FormFile:

    """ File wrapper around XML, to cater for relative paths """

    def __init__(self, filename, _prefix=None):
        
        path = self.get_path_from_prefix(_prefix)

        self.filename = os.path.join(path, filename)

        if not os.path.isfile(self.filename):
            raise ValueError("No such file", self.filename)


    def modified(self):

        """ Return last modified timestamp """

        return os.path.getmtime(self.filename)


    def get_path_from_prefix(self, _prefix):

        if isinstance(_prefix, str):
            path = _prefix
        else:
            if _prefix is None:
                _prefix = sys._getframe(2).f_globals
            path = os.path.dirname(_prefix['__file__'])

        return path
