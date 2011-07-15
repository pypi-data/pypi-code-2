import datetime
import hashlib
import os
import logging
import sys
import time
from subprocess import Popen

log = logging.getLogger(__name__)

def set_time(path, accessed, modified):
    # This doesn't seem to work on directories
    if isinstance(accessed, datetime.datetime):
        accessed = time.mktime(accessed.timetuple())
    if isinstance(modified, datetime.datetime):
        modified = time.mktime(modified.timetuple())
    if not isinstance(accessed, (int, float)):
        raise Exception('Expected a datatime, int or float object to set the accessed time for %r, not %r'%(path, accessed))
    if not isinstance(modified, (int, float)):
        raise Exception('Expected a datatime, int or float object to set the modified time for %r, not %r'%(path, modified))
    log.debug('Setting %r accessed time to %s and modified time to %s', path, accessed, modified)
    os.utime(
        path,
        (
            accessed,
            modified,
        )
    )

# We use 16*1024 as the size because that's what shutil.copyfileobj() uses,
# so it should be a sensible default.
def sha1(src, size=16*1024, skip_revert_times=False):
    log.debug('Generating a sha1 hash for %r', src)
    h = hashlib.new('sha1')
    stat_src = os.stat(src)
    f = open(src, "rb")
    try:
        chunk = f.read(size)
        while chunk: # EOF condition
            h.update(chunk)
            chunk = f.read(size)
    except Exception, e:
        log.error('Could not generate hash %r. Error was %r', src, e)
        raise
    else:
        # Put the source time back to how it was. @@@ is this a good idea?
        if not skip_revert_times:
            try:
                set_time(
                    src, 
                    stat_src.st_atime, 
                    stat_src.st_mtime,
                )
            except Exception, e:
                log.error(
                    'Could not reset the modification time on %r. Error was %r', 
                    src,
                    e,
                )
        return h.hexdigest()
    finally:
        f.close()

