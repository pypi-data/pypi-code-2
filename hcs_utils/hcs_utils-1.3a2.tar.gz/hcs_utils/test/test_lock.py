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

import os
import socket

from hcs_utils.lock import Lock, LockError
from hcs_utils.path import tempdir
from hcs_utils.unittest import eq_
from py.test import raises

def test_1():
    with tempdir() as tmpd:
        lockn = os.path.join(tmpd, 'lockfile')
        lock = Lock(lockn)
        eq_(lock.testlock(), None)
        lock.lock()
        assert os.path.islink(lockn)
        eq_(len(lock.testlock()), 2)
        lock.release()
        eq_(lock.testlock(), None)

def test_2():
    with tempdir() as tmpd:
        lockn = os.path.join(tmpd, 'lockfile')
        with Lock(lockn) as lock:
            eq_(len(lock.testlock()), 2)
            assert os.path.islink(lockn)

def test_locked_on_other_host():
    with tempdir() as tmpd:
        lockn = os.path.join(tmpd, 'lockfile')

        #create broken lock
        os.symlink('other_host:123456789', lockn)

        lock = Lock(lockn)
        with raises(LockError):
            lock.lock()

def test_break_lock():
    with tempdir() as tmpd:
        lockn = os.path.join(tmpd, 'lockfile')

        #create broken lock
        os.symlink(socket.gethostname() + ':123456789', lockn)

        lock = Lock(lockn)
        lock.lock()
