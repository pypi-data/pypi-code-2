#
# Helper FileUpload class for the test suite
#

from OFS.SimpleItem import SimpleItem
from ZPublisher.HTTPRequest import FileUpload


class FileUpload(FileUpload):
    """Dummy upload object.

    Used to fake uploaded files and images.
    """

    __allow_access_to_unprotected_subobjects__ = 1

    filename = 'dummy.gif'
    headers = {}

    def __init__(self, filename=None, headers=None, file=None):
        self.file = file
        if filename is not None:
            self.filename = filename
        if headers is not None:
            self.headers = headers

    def seek(self,*args):
        return self.file.seek(*args)

    def tell(self,*args):
        return self.file.tell(*args)

    def read(self,*args):
        return self.file.read(*args)
