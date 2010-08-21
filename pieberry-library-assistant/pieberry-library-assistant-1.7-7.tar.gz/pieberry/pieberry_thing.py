from pybtex.core import Entry, Person


class Thing(Entry):
    '''Interface class for passing document data around, inherits
    pybtex's Entry type for ease of conversion & storage'''

    def __init__(self, type_, fields=None, persons=None, collection=None):
        pass
