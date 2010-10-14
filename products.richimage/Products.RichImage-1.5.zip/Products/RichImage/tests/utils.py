from os.path import dirname, join
from Products.RichImage import tests


def getFile(filename):
    """ return a file object from the test data folder """
    filename = join(dirname(tests.__file__), 'input', filename)
    return open(filename, 'rb')

