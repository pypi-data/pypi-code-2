import tempfile
import os

def init_tempdir(tempdir):
    if not os.path.exists(tempdir):
        msg = 'Cannot set the temporary directory %s because it doesn t exist' % tempdir
        raise ValueError(msg)

    tempfile.tempdir = tempdir

