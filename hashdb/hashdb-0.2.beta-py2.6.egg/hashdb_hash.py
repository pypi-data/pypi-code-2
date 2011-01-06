#!/usr/bin/python

from hashdb_output import log, isatty
import hashdb_onsigint
import hashdb_progress
import hashlib
import sys

def build_hash(target, width=None):
    hasher = hashlib.md5()
    if target.stat.st_size == 0:
        return 'd41d8cd98f00b204e9800998ecf8427e' # doesn't just speed up zero byte files. Unending files are also reported as 0 bytes long

    display = log.is_verbose and isatty(sys.stdout) and (target.stat.st_size > 2**20)
    if display:
        if width == None:
            width = hashdb_progress.find_terminal_width()
        total = 0
    try:
        if display:
            print '\x1B[?25l\r', # hide cursor
            print hashdb_progress.build_progress(total, target.stat.st_size, width) + '\r',

        with open(target.true, 'rb') as f:
            while True:
                data = f.read(2**17)
                if not data:
                    break
                hasher.update(data)

                if display:
                    total += len(data)
                    print hashdb_progress.build_progress(total, target.stat.st_size, width) + '\r',

        if display:
            print hashdb_progress.build_progress(target.stat.st_size, target.stat.st_size, width) + '\r',
            print '\x1B[?25h' # display cursor

        return hasher.hexdigest()

    except OSError, ex:
        log.warning('warning: Unable to hash file %r: %s' % (target.user, ex))
    except IOError, ex:
        log.warning('warning: Unable to hash file %r: %s' % (target.user, ex))


if __name__ == '__main__':
    import hashdb_walk
    w = hashdb_walk.Walker()
    w.add_target('test/Burn.Notice.S04E18.Last.Stand.HDTV.XviD-FQM.[VTV].avi')

    hash = build_hash(w._targets[0])
    print '\x1B[0K' + hash + '  %s' % w._targets[0].user # clear line and display has

