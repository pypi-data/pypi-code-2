import datetime
import hashlib
import os
import logging
import sys
import time
from subprocess import Popen

log = logging.getLogger(__name__)

def set_time(path, accessed, modified):
    if os.path.isdir(path):
        cmd = ['touch', '-d', modified.strftime("%Y-%m-%d %H:%M:%S.%f"),  '-m', path.encode(sys.getfilesystemencoding())]
        log.info(' '.join([str(x) for x in cmd]))
        process = Popen(cmd)
        log.error('%s', process.communicate())
        result = process.wait()
        if result:
            log.error('Could not set modify time on %r', path)
        cmd = ['touch', '-d', accessed.strftime("%Y-%m-%d %H:%M:%S.%f"),  '-a', path.encode(sys.getfilesystemencoding())]
        log.info(' '.join([str(x) for x in cmd]))
        process = Popen(cmd)
        log.error('%s', process.communicate())
        result = process.wait()
        if result:
            log.error('Could not set accessed time on %r', path)
    else:
        # This doesn't seem to work on directories
        if isinstance(accessed, datetime.datetime):
            accessed = time.mktime(accessed.timetuple())
        if isinstance(modified, datetime.datetime):
            modified = time.mktime(modified.timetuple())
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

