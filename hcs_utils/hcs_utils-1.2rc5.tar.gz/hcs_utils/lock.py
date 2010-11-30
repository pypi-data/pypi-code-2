# -*- coding: UTF-8 -*-
# vim: fileencoding=UTF-8 filetype=python ff=unix et ts=4 sw=4 sts=4 tw=120
#
# Copyright (c) 2010, Christer Sjöholm -- hcs AT furuvik DOT net
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import errno
import logging
import os
import socket

class Lock(object):
    '''
    Interprocess locking using a PID file (symlink actually).

    - Supports locks on NFS
    - Has support for breaking stale locks of processes on the same host.


    A lock ID looks like this: HOST:PID
    '''
    log = logging.getLogger(__name__)

    def __init__(self, pathname):
        self.pathname = pathname
        self.hostname = socket.gethostname()

    def __enter__(self):
        self.lock()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()

    def lock(self):
        locker = '%s:%d' % (self.hostname, os.getpid())
        try:
            if self.testlock():
                raise LockError('Already locked: %s' % self.pathname)
            return os.symlink(locker, self.pathname)
        except OSError, err:
            raise LockError('Failed to create lock: %s' % self.pathname, err)

    def release(self):
        if self.has_lock():
            os.unlink(self.pathname)
        elif self.testlock() == None:
            raise LockError('Tried to release non existing.')
        else:
            raise LockError('Tried to release someone elses lock.')

    def has_lock(self):
        '''
        returns True if this process has the lock, otherwise False.
        '''
        lock = self.testlock()
        if lock and lock == (self.hostname, os.getpid()):
            return True
        else:
            return False

    def testlock(self):
        """return (host, pid) if locked, else None.
        If the lock is invalid it is removed and None is returned.

        """
        try:
            host, pid = os.readlink(self.pathname).split(':', 1)
            pid = int(pid)
        except OSError, err:
            if err.errno == errno.ENOENT:
                return None
            raise LockError('Failed to read lock: %s' % self.pathname, err)
        if host != self.hostname or check_pid(pid):
            return host, pid
        # Lock the lock before breaking it.
        try:
            with Lock(self.pathname + '.break'):
                os.unlink(self.pathname)
        except LockError:
            return host, pid

def check_pid(pid):
    '''Check if the process exists'''
    try:
        os.kill(pid, 0)
        return True # Process alive
    except OSError:
        return False

class LockError(Exception):
    pass
