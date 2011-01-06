#!/usr/bin/python

from hashdb_output import log

try:
    from hashdb_mntent import mntent, setmntent, getmntent_r, endmntent
    import ctypes
except:
    log.debug('failed to load mntent stubs')
    setmntent = lambda filename: None

import os
from collections import namedtuple

MountEntry = namedtuple('MountEntry', 'fsname dir type opts freq passno')

def enum_mntent(filename):
    stream = setmntent(filename)
    if not stream:
        return []

    try:
        buf    = ctypes.create_string_buffer(4095)
        mount  = mntent()
        results = []
        while getmntent_r(stream, mount, ctypes.byref(buf), ctypes.sizeof(buf) - 1):
            results.append(MountEntry(
                mount.mnt_fsname,
                mount.mnt_dir,
                mount.mnt_type,
                set(mount.mnt_opts.split(',')),
                mount.mnt_freq,
                mount.mnt_passno,
            ))
        return results
    finally:
        endmntent(stream)

class MountEntries(object):
    entries_mtab         = None
    entries_mounts       = None
    entries_mtab_bydir   = None
    entries_mounts_bydir = None

    def __init__(self):
        object.__init__(self)

        self.load()

    def load(self):
        self.entries_mtab   = enum_mntent('/etc/mtab') or []
        self.entries_mounts = enum_mntent('/proc/mounts') or []
        self.entries_mtab_bydir   = dict((mount.dir, mount) for mount in self.entries_mtab)
        self.entries_mounts_bydir = dict((mount.dir, mount) for mount in self.entries_mounts)

    def is_bind(self, path):
        assert(os.path.isabs(path))
        return (path in self.entries_mtab_bydir) and ('bind' in self.entries_mtab_bydir[path].opts)

    def get_mount(self, path):
        assert(os.path.isabs(path))
        bits = path.split(os.sep)
        for i in reversed(range(1, len(bits))):
            lhs = os.path.join(*bits[:i])

            if lhs in self.entries_mounts_bydir:
                return (self.entries_mounts_bydir[lhs], os.path.join(*bits[i:]))
        return (None, path)

    def _truepath_abs(self, path):
        path = os.path.realpath(path)
        path = os.path.normpath(path)
        mount, path = self.get_mount(path)
        if mount:
            mount_bind = self.entries_mtab_bydir.get(mount.dir)
            if (mount_bind != None) and (os.path.isabs(mount_bind.fsname)):
                path = os.path.join(mount_bind.fsname, path)
                path = self._truepath_abs(path)
            else:
                path = os.path.join(mount.dir, path)
        return path

    def truepath(self, path):
        path = os.path.join(os.getcwd(), path)
        path = self._truepath_abs(path)
        return path

    def get_fstype(self, path):
        assert(os.path.isabs(path))
        name = None
        while True:
            if path in self.entries_mounts_bydir:
                return self.entries_mounts_bydir[path]
            if name == '':
                break

            path, name = os.path.split(path)
        return None

    def __str__(self):
        return '; /etc/mtab\n' + ''.join('%s\n' % (m,) for m in self.entries_mtab) + '; /proc/mounts\n' + ''.join('%s\n' % (m,) for m in self.entries_mounts)

if __name__ == '__main__':
    mounts = MountEntries()
    print mounts