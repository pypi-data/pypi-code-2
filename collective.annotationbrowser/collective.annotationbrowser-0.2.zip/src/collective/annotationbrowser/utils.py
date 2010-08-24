from BTrees.OOBTree import OOBTree
from BTrees.IOBTree import IOBTree

def custom_repr(value):
    """ Represent different types as string values. 
        Example: <BTrees._OOBTree.OOBTree object at 0x10acb59d0>
            is represented as OOBTree keys
        Common cases are handled automatically (strings, numbers, ...)
    """
    if isinstance(value, (OOBTree, IOBTree)):
        result = list(value.keys())
    else:
        result = value
        
    # determine "length" of a value
    try:
        as_string = str(result)
    except UnicodeError:
        try:
            as_string = unicode(result)
        except:
            as_string = 'UNKNOWN ENCODING'
    return as_string
    