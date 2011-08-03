# Copyright (c) 2010 Florian Friesdorf <flo@chaoflow.net>
# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import errno
import fnmatch
import logging
import os
import restarter


class Proc:
    """Represent a process identified by a pidfile.

    Processes may be running or not running. If running, we can examine them for
    stale executables or memory mapped objects.
    """

    def __init__(self, pidfile, pid, exclude=None):
        self.pidfile = pidfile
        self.pid = pid
        self.exclude = exclude
        self.exe = None
        self.maps = None
        self.log = logging.getLogger('restarter')

    def __eq__(self, other):
        return self.pidfile == other.pidfile and self.pid == other.pid

    @property
    def stale(self):
        """Determine if this process has any stale objects."""
        return self.stale_exe() or self.stale_maps()

    def stale_exe(self):
        """Determine if the executable is stale."""
        if not os.access(self.exe, os.F_OK):
            self.log.info('stale exe {}'.format(self.exe))
            return True
        return False

    def stale_maps(self):
        """Determine if there are any stale (non-excluded) mmap'ed objects."""
        for line in self.maps.split('\n'):
            try:
                filename = line.split(None, 5)[5]
            except IndexError:
                continue
            if not filename.startswith('/'):
                continue
            if (not self.match_exclude(filename) and
                not os.access(filename, os.F_OK)):
                self.log.info('stale mmap {}'.format(filename))
                return True
        return False

    def match_exclude(self, filename):
        """Filter object list for exceptions.

        Exclude expressions may be specified as prefixes (e.g., /lib/libc) or
        shell glob expressions. Please note that the kernel tends to add some
        informative string to stale objects (e.g., "(deleted)"), so be sure to
        leave the suffix variable.
        """

        if self.exclude:
            if any(filename.startswith(e) for e in self.exclude):
                return True
            if any(fnmatch.fnmatch(filename, e) for e in self.exclude):
                return True
        return False

    def reread(self):
        """Reread pidfile and return new Proc object with up-to-date status."""
        return readpid(self.pidfile)


def readpid(pidfile, exclude=None):
    """Factory to create Proc objects from pidfiles."""
    log = logging.getLogger('restarter')
    try:
        pid = int(open(pidfile).read().strip())
        proc = Proc(pidfile, pid, exclude)
        proc.exe = os.readlink('/proc/{}/exe'.format(pid)).strip()
        proc.maps = open('/proc/{}/maps'.format(pid)).read()
        return proc
    except EnvironmentError as e:
        log.info('service not running: cannot open {}'.format(e.filename))
        raise restarter.PidfileError(e.errno, e.strerror, e.filename)
    except ValueError as e:
        log.info('invalid pidfile')
        raise restarter.PidfileError(errno.EINVAL, str(e), pidfile)
