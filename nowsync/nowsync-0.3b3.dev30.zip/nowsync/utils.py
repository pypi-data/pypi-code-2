import os

def _relpath(path, start=os.path.curdir):
    """Return a relative version of a path
    
    Backported from Python2.7, Python2.5 does not have this function
    
    """

    if not path:
        raise ValueError("no path specified")

    start_list = [x for x in os.path.abspath(start).split(os.path.sep) if x]
    path_list = [x for x in os.path.abspath(path).split(os.path.sep) if x]

    # Work out how much of the filepath is shared by start and path.
    i = len(os.path.commonprefix([start_list, path_list]))

    rel_list = [os.path.pardir] * (len(start_list)-i) + path_list[i:]
    if not rel_list:
        return os.path.curdir
    return os.path.join(*rel_list)

try:
    from os.path import relpath
except ImportError:
    relpath = _relpath