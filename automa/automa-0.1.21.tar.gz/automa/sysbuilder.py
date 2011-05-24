#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: t -*-
#
# Copyright (C) 2011 Marco Pantaleoni. All rights reserved
# Marco Pantaleoni <marco.pantaleoni@gmail.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 2 as
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

__author__    = "Marco Pantaleoni"
__copyright__ = "Copyright (C) 2011 Marco Pantaleoni"
__license__   = "GPL v2"

#import subprocess
import sys, os
import re

from automa.opts import options, Options
from automa.tasks import TaskContext, task, depends, cmdline, call_task
from automa.path import Path
from automa.shell import sh, cd
from automa.configfile import ConfigParser, ConfigAction, ConfigSection
from automa.utils import *
from automa.log import *

# ========================================================================
#   CONSTANTS
# ========================================================================

DEFAULT_TARGET_NAME = "DEFAULT"

PACKAGESPEC_VERSION_RE = re.compile(r'^([a-zA-Z0-9-]+)-([0-9]+[0-9\.]*[a-zA-Z0-9]*)$')

TARGET_I486_UCLIBC_TRIPLET = "i486-pc-linux-uclibc"
TARGET_I486_UCLIBC_LIBC    = "uclibc"
TARGET_I486_UCLIBC_CPU     = "i486"
TARGET_I486_UCLIBC_COMPILER_CPU = "i486"
TARGET_I486_UCLIBC_NAME    = "i486"
TARGET_I486_UCLIBC_ENDIAN  = "little"
TARGET_I486_UCLIBC_NOTE    = "Intel's i486, uClibc (486 compatibles)"

TARGET_I486_UCLIBC = dict(triplet=TARGET_I486_UCLIBC_TRIPLET,
                          name=TARGET_I486_UCLIBC_NAME,
                          cpu=TARGET_I486_UCLIBC_CPU,
                          compiler_cpu=TARGET_I486_UCLIBC_COMPILER_CPU,
                          libc=TARGET_I486_UCLIBC_LIBC,
                          endian=TARGET_I486_UCLIBC_ENDIAN,
                          note=TARGET_I486_UCLIBC_NOTE)

TARGET_VORTEX86_UCLIBC_TRIPLET = "i486-pc-linux-uclibc"
TARGET_VORTEX86_UCLIBC_LIBC    = "uclibc"
TARGET_VORTEX86_UCLIBC_CPU     = "i486"
TARGET_VORTEX86_UCLIBC_COMPILER_CPU = "i486"
TARGET_VORTEX86_UCLIBC_NAME    = "vortex86"
TARGET_VORTEX86_UCLIBC_ENDIAN  = "little"
TARGET_VORTEX86_UCLIBC_NOTE    = "Vortex86 SX/DS, uClibc (486 compatible with TSC)"

TARGET_VORTEX86_UCLIBC = dict(triplet=TARGET_VORTEX86_UCLIBC_TRIPLET,
                              name=TARGET_VORTEX86_UCLIBC_NAME,
                              cpu=TARGET_VORTEX86_UCLIBC_CPU,
                              compiler_cpu=TARGET_VORTEX86_UCLIBC_COMPILER_CPU,
                              libc=TARGET_VORTEX86_UCLIBC_LIBC,
                              endian=TARGET_VORTEX86_UCLIBC_ENDIAN,
                              note=TARGET_VORTEX86_UCLIBC_NOTE)

TARGET_I586_UCLIBC_TRIPLET = "i586-pc-linux-uclibc"
TARGET_I586_UCLIBC_LIBC    = "uclibc"
TARGET_I586_UCLIBC_CPU     = "i586"
TARGET_I586_UCLIBC_COMPILER_CPU = "i586"
TARGET_I586_UCLIBC_NAME    = "i586"
TARGET_I586_UCLIBC_ENDIAN  = "little"
TARGET_I586_UCLIBC_NOTE    = "Intel Pentium without MMX, uClibc (Pentium, K6, 586 Compatibles)"

TARGET_I586_UCLIBC = dict(triplet=TARGET_I586_UCLIBC_TRIPLET,
                          name=TARGET_I586_UCLIBC_NAME,
                          cpu=TARGET_I586_UCLIBC_CPU,
                          compiler_cpu=TARGET_I586_UCLIBC_COMPILER_CPU,
                          libc=TARGET_I586_UCLIBC_LIBC,
                          endian=TARGET_I586_UCLIBC_ENDIAN,
                          note=TARGET_I586_UCLIBC_NOTE)

TARGET_I686_UCLIBC_TRIPLET = "i686-pc-linux-uclibc"
TARGET_I686_UCLIBC_LIBC    = "uclibc"
TARGET_I686_UCLIBC_CPU     = "i686"
TARGET_I686_UCLIBC_COMPILER_CPU = "i686"
TARGET_I686_UCLIBC_NAME    = "i686"
TARGET_I686_UCLIBC_ENDIAN  = "little"
TARGET_I686_UCLIBC_NOTE    = "Pentium Pro instruction set, uClibc (Pentium Pro, Pentium II, Pentium III, Pentium 4)"

TARGET_I686_UCLIBC = dict(triplet=TARGET_I686_UCLIBC_TRIPLET,
                          name=TARGET_I686_UCLIBC_NAME,
                          cpu=TARGET_I686_UCLIBC_CPU,
                          compiler_cpu=TARGET_I686_UCLIBC_COMPILER_CPU,
                          libc=TARGET_I686_UCLIBC_LIBC,
                          endian=TARGET_I686_UCLIBC_ENDIAN,
                          note=TARGET_I686_UCLIBC_NOTE)

TARGET_ATHLON_UCLIBC_TRIPLET = "i686-pc-linux-uclibc"
TARGET_ATHLON_UCLIBC_LIBC    = "uclibc"
TARGET_ATHLON_UCLIBC_CPU     = "i686"
TARGET_ATHLON_UCLIBC_COMPILER_CPU = "athlon"
TARGET_ATHLON_UCLIBC_NAME    = "athlon"
TARGET_ATHLON_UCLIBC_ENDIAN  = "little"
TARGET_ATHLON_UCLIBC_NOTE    = "AMD 32 bit Athlon, uClibc"

TARGET_ATHLON_UCLIBC = dict(triplet=TARGET_ATHLON_UCLIBC_TRIPLET,
                            name=TARGET_ATHLON_UCLIBC_NAME,
                            cpu=TARGET_ATHLON_UCLIBC_CPU,
                            compiler_cpu=TARGET_ATHLON_UCLIBC_COMPILER_CPU,
                            libc=TARGET_ATHLON_UCLIBC_LIBC,
                            endian=TARGET_ATHLON_UCLIBC_ENDIAN,
                            note=TARGET_ATHLON_UCLIBC_NOTE)

TARGET_OPTERON_UCLIBC_TRIPLET = "x86_64-unknown-linux-uclibc"
TARGET_OPTERON_UCLIBC_LIBC    = "uclibc"
TARGET_OPTERON_UCLIBC_CPU     = "x86_64"
TARGET_OPTERON_UCLIBC_COMPILER_CPU = "k8"
TARGET_OPTERON_UCLIBC_NAME    = "k8"
TARGET_OPTERON_UCLIBC_ENDIAN  = "little"
TARGET_OPTERON_UCLIBC_NOTE    = "AMD K8 processors with x86-64, uClibc"

TARGET_OPTERON_UCLIBC = dict(triplet=TARGET_OPTERON_UCLIBC_TRIPLET,
                             name=TARGET_OPTERON_UCLIBC_NAME,
                             compiler_cpu=TARGET_OPTERON_UCLIBC_COMPILER_CPU,
                             cpu=TARGET_OPTERON_UCLIBC_CPU,
                             libc=TARGET_OPTERON_UCLIBC_LIBC,
                             endian=TARGET_OPTERON_UCLIBC_ENDIAN,
                             note=TARGET_OPTERON_UCLIBC_NOTE)

TARGETS = {
    TARGET_I486_UCLIBC_NAME:     TARGET_I486_UCLIBC,
    TARGET_VORTEX86_UCLIBC_NAME: TARGET_VORTEX86_UCLIBC,
    TARGET_I586_UCLIBC_NAME:     TARGET_I586_UCLIBC,
    TARGET_I686_UCLIBC_NAME:     TARGET_I686_UCLIBC,
    TARGET_ATHLON_UCLIBC_NAME:   TARGET_ATHLON_UCLIBC,
    TARGET_OPTERON_UCLIBC_NAME:  TARGET_OPTERON_UCLIBC,
}

TARGET_SYS_NAME = TARGET_VORTEX86_UCLIBC_NAME

# ========================================================================
#
#   Helper classes and functions
#
# ========================================================================

def _str_to_list(text):
    return [el.strip() for el in text.split(',')]

class PackageSpec(object):
    """
    A package specification.
    It comprises a ``name`` and a ``version``.
    The ``version`` can be left unspecified, thus being None.
    """
    def __init__(self, packagespec=None, name=None, version=None):
        self.spec    = packagespec
        self.name    = name
        self.version = version or None

        self.major   = None
        self.minor   = None
        self.micro   = None
        self.extraversion = None

        if packagespec:
            if isinstance(packagespec, (tuple, list)):
                self.name    = packagespec[0]
                self.version = packagespec[1]
            elif isinstance(packagespec, dict):
                self.name = packagespec['name']
                self.version = packagespec['version']
            elif isinstance(packagespec, PackageSpec):
                self.spec = packagespec.spec
                self.name = packagespec.name
                self.version = packagespec.version
            elif isinstance(packagespec, basestring) or isinstance(packagespec, Path):
                packagespec = str(packagespec)
                m = PACKAGESPEC_VERSION_RE.match(packagespec)
                if m:
                    (self.name, self.version) = m.groups()
                else:
                    self.name = packagespec
            else:
                raise "package specification format unknown in %r" % packagespec

        self._parse_version()

    def __str__(self):
        if self.version:
            return "%s-%s" % (self.name, self.version)
        return "%s" % self.name

    def __repr__(self):
        return "<PackageSpec %r v:%r>" % (self.name, self.version)

    @property
    def version_number(self):
        value = 0
        if self.major:
            try:
                v = int(self.major)
            except ValueError:
                return -1
            value += (v * 10000)
        if self.minor:
            try:
                v = int(self.minor)
            except ValueError:
                return -1
            value += (v * 100)
        if self.micro:
            try:
                v = int(self.micro)
            except ValueError:
                return -1
            value += v
        return value

    def _parse_version(self):
        if self.version:
            components = self.version.split('.')
            if len(components) > 0:
                self.major = components[0]
            if len(components) > 1:
                self.minor = components[1]
            if len(components) > 2:
                self.micro = components[2]
            if len(components) > 3:
                self.extraversion = '.'.join(self.version.split('.')[3:])
            else:
                self.extraversion = ""
        return self

    def __copy__(self):
        return PackageSpec(packagespec=self)

class IncludeConfigParser(ConfigParser):
    """
    automa.sysbuilder IncludeConfigParser

    It is used to load sysbuilder (system and package) configuration files.
    It handles 'include' actions.
    """

    def __init__(self, configfile, opts=None, root=None, base_include_dir=None):
        super(IncludeConfigParser, self).__init__(configfile, opts=opts, root=root)
        self.base_include_dir = base_include_dir

    def resolve_include_path(self, includepath):
        includepath_obj = Path(includepath)
        if includepath_obj.isabs:
            return includepath
        if not self.base_include_dir:
            return includepath
        assert self.base_include_dir
        if isinstance(self.base_include_dir, (tuple, list)):
            for base_dir in self.base_include_dir:
                includepath_obj = Path(base_dir) / includepath
                if includepath_obj.exists:
                    return includepath_obj.pathname
        else:
            includepath_obj = Path(self.base_include_dir) / includepath
            return includepath_obj.pathname
        return includepath

    def handle_include(self, entry):
        assert isinstance(entry, ConfigAction)
        pathname = self.resolve_include_path(entry.value)
        cparser = IncludeConfigParser(pathname, opts=self.opts, root=self.root,
                                      base_include_dir=self.base_include_dir)
        cparser.parse()
        return self


def resolve_package_config(packagespec):
    """
    Return the Path corresponding to the most suitable package configuration
    file for the package described by ``packagespec``, or None.

    If ``packagespec`` includes a package version qualifier, than only
    the package config file for that version is took into consideration.

    It a version qualifier is missing, than the highest numbered version is
    returned.
    """
    pspec = PackageSpec(packagespec)

    base_pkgconfig_dir = options.sysbuilder.package_config_dir
    if not isinstance(base_pkgconfig_dir, (tuple, list)):
        base_pkgconfig_dir = [base_pkgconfig_dir,]

    for pkgconfig_dir in base_pkgconfig_dir:
        if pspec.version:
            pkgconfig_v_glob = Path(pkgconfig_dir) / ("%s/%s-%s.conf" % (pspec.name, pspec.name, pspec.version))
            pkgconfig_glob = Path(pkgconfig_dir) / ("%s/%s.conf" % (pspec.name, pspec.name))
            all_pkgconfig_objs = pkgconfig_v_glob.glob() + pkgconfig_glob.glob()
        else:
            pkgconfig_v_glob = Path(pkgconfig_dir) / ("%s/%s-*.conf" % (pspec.name, pspec.name))
            pkgconfig_glob = Path(pkgconfig_dir) / ("%s/%s.conf" % (pspec.name, pspec.name))
            all_pkgconfig_objs = pkgconfig_v_glob.glob() + pkgconfig_glob.glob()
        highest_version = None
        highest_pkgconfig = None
        for pkgconfig_obj in all_pkgconfig_objs:
            if pkgconfig_obj.exists:
                (t1, t2) = pkgconfig_obj.splitext()
                spec = PackageSpec(t1.basename)
                if (highest_version is None) or (spec.version_number > highest_version):
                    highest_version = spec.version_number
                    highest_pkgconfig = pkgconfig_obj
        if highest_pkgconfig and highest_pkgconfig.exists:
            debug("resolve_package_config(%r) -> %r" % (packagespec, highest_pkgconfig))
            return highest_pkgconfig
    return None

root_section = None

class PackageConfig(object):
    """
    Package configuration object.

    This keeps a PackageSpec object for the package (``spec`` member variable),
    and it loads the most suitable configuration file in a
    automa.configfile.ConfigSection instance (``config_section`` member
    variable).
    """

    _db = None

    def __init__(self, packagespec):
        PackageConfig._db_init()

        self.spec           = None
        self.actual_spec    = None
        self.config_path    = None
        self.config_section = None
        self.needs          = None

        self._built     = False
        self._installed = False

        if isinstance(packagespec, PackageConfig):
            self.spec           = packagespec.spec
            self.actual_spec    = packagespec.actual_spec
            self.config_path    = packagespec.config_path
            self.config_section = packagespec.config_section
            self.needs          = packagespec.needs
            self._built         = packagespec._built
            self._installed     = packagespec._installed
        else:
            self.spec = PackageSpec(packagespec)
            self._load_config_file()

        self._db_register()

    def __str__(self):
        return str(self.spec)

    def __repr__(self):
        extra_info = ""
        if self.config_path:
            extra_info += " config file:'%s'" % self.config_path
        if self.ok:
            extra_info += " ok"
        else:
            extra_info += " ERROR"
        if self.config_section and self.native:
            extra_info += " native"
        if self.built:
            extra_info += " built"
        if self.installed:
            extra_info += " installed"
        if self.needs:
            extra_info += " needs:%s" % repr(self.needs)
        if self.actual_spec:
            return "<PackageConfig for '%s' (actual:'%s')%s>" % (self.spec, self.actual_spec, extra_info)
        return "<PackageConfig for '%s'%s>" % (self.spec, extra_info)

    # -- PACKAGE DB SERIALIZATION --------------------------------------------

    def __getstate__(self):
        return {
            'spec': self.spec,
            'actual_spec': self.actual_spec,
            '_built': self._built,
            '_installed': self._installed,
        }

    def __setstate__(self, state):
        assert isinstance(state, dict)
        self.spec        = state['spec']
        self.actual_spec = state['actual_spec']
        self._built      = state['_built']
        self._installed  = state['_installed']
        self._load_config_file()

    @classmethod
    def _db_filename(cls):
        return ".packagedb-%s" % options.sysbuilder.target

    @classmethod
    def _db_init(cls):
        if cls._db is None:
            cls._db = {}
            filename = cls._db_filename()
            p = Path(filename)
            if p.exists:
                cls._db_load()
                return cls
        return cls

    @classmethod
    def _db_remove(cls):
        filename = cls._db_filename()
        p = Path(filename)
        if p.exists:
            p.nuke()
        return cls

    @classmethod
    def _db_load(cls):
        try:
            from cPickle import load
        except ImportError:
            from pickle import load
        filename = cls._db_filename()
        p = Path(filename)
        if not p.exists:
            return cls
        f = open(filename, 'rb')
        cls._db = load(f)
        f.close()
        debug("Loaded PackageConfig DB:%r" % repr(cls._db))
        return cls

    @classmethod
    def _db_save(cls):
        try:
            from cPickle import dump
        except ImportError:
            from pickle import dump
        filename = cls._db_filename()
        f = open(filename, 'wb')
        dump(cls._db, f)
        f.close()
        return cls

    @classmethod
    def Has(cls, pkgspec_or_pkgconfig):
        assert isinstance(pkgspec_or_pkgconfig, PackageSpec) or isinstance(pkgspec_or_pkgconfig, PackageConfig) or isinstance(pkgspec_or_pkgconfig, basestring)
        key = cls._DB_key(pkgspec_or_pkgconfig)
        return cls._db.has_key(key)

    @classmethod
    def Get(cls, pkgspec_or_pkgconfig):
        assert isinstance(pkgspec_or_pkgconfig, PackageSpec) or isinstance(pkgspec_or_pkgconfig, PackageConfig) or isinstance(pkgspec_or_pkgconfig, basestring)
        pkgconfig = None
        if isinstance(pkgspec_or_pkgconfig, PackageSpec):
            key = cls._DB_key(pkgspec_or_pkgconfig)
            if cls._db.has_key(key):
                return cls._db[key]
            pkgconfig = PackageConfig(pkgspec_or_pkgconfig)
            key = cls._DB_key(pkgconfig)
            if cls._db.has_key(key):
                return cls._db[key]
            cls._db[key] = pkgconfig
            cls._db_save()
            return pkgconfig
        elif isinstance(pkgspec_or_pkgconfig, PackageConfig):
            import copy
            pkgconfig = pkgspec_or_pkgconfig
            key = cls._DB_key(pkgconfig.actual_spec)
            if cls._db.has_key(key):
                return cls._db[key]
            pkgconfig = copy.copy(pkgconfig)
            cls._db[key] = pkgconfig
            cls._db_save()
            return pkgconfig
        elif isinstance(pkgspec_or_pkgconfig, basestring):
            pkgconfig = PackageConfig(pkgspec_or_pkgconfig)
            key = cls._DB_key(pkgconfig.actual_spec)
            if cls._db.has_key(key):
                return cls._db[key]
            cls._db[key] = pkgconfig
            cls._db_save()
            return pkgconfig
        assert False
        return pkgspec_or_pkgconfig

    @classmethod
    def DB_Packages(cls):
        """Return a list of PackageConfig instances for all packages inside the DB."""
        return [cls.Get(k) for k in cls._db.keys()]

    def _db_register(self):
        if not PackageConfig.Has(self):
            key = PackageConfig._DB_key(self)
            PackageConfig._db[key] = self
            PackageConfig._db_save()
        return self

    @classmethod
    def _DB_key(cls, pkgspec_or_pkgconfig):
        assert isinstance(pkgspec_or_pkgconfig, PackageSpec) or isinstance(pkgspec_or_pkgconfig, PackageConfig) or isinstance(pkgspec_or_pkgconfig, basestring)
        if isinstance(pkgspec_or_pkgconfig, PackageSpec):
            return "%s" % pkgspec_or_pkgconfig
        elif isinstance(pkgspec_or_pkgconfig, PackageConfig):
            return "%s" % pkgspec_or_pkgconfig.actual_spec
        elif isinstance(pkgspec_or_pkgconfig, basestring):
            return "%s" % pkgspec_or_pkgconfig
        assert False
        return pkgspec_or_pkgconfig

    @property
    def _db_key(self):
        return self._DB_key(self)

    # ---PACKAGE DB SERIALIZATION / end --------------------------------------

    def _get_built(self):
        return self._built
    def _set_built(self, value):
        self._built = value
        self._db_save()
    built = property(_get_built, _set_built, None, "``built`` property")

    def _get_installed(self):
        return self._installed
    def _set_installed(self, value):
        self._installed = value
        self._db_save()
    installed = property(_get_installed, _set_installed, None, "``installed`` property")

    @property
    def native(self):
        native = self.config_section.get('native', False)
        if native in (False, None, "no", "false", "f", "0"):
            return False
        return native

    @property
    def ok(self):
        return (self.config_section is not None)

    @property
    def package_tarball(self):
        """Return the Path for the package tarball."""
        cache_dir = Path(options.sysbuilder.package_dir)
        url       = self.config_section.url
        filename  = url2filename(url)
        return cache_dir / filename

    @property
    def package_extracted_dirname(self):
        """
        Return the toplevel directory name (without leading components) for
        the extracted tarball.
        """
        dirname = self.config_section.get('extract_dir', "%s" % self.actual_spec)
        return dirname

    @property
    def package_source_directory(self):
        """Return the Path for the package source/build directory."""
        source_dir = Path(options.sysbuilder.build_dir)
        return source_dir / self.package_extracted_dirname

    @property
    def package_binary_tarball(self):
        """Return the Path for the package compiled tarball."""
        return Path(options.sysbuilder.package_binary_dir) / ("%s-binary-%s-%s-%s.tar.bz2" % (self.actual_spec.name, options.sysbuilder.target, options.sysbuilder.CLFS_TARGET, self.actual_spec.version))

    def _load_config_file(self):
        """
        Load the proper config file for the package, if such a file exists, and
        save the correspoding automa.configfile.ConfigSection

        If the config file is found and loaded return True, otherwise
        return None.
        """
        debug("PackageConfig._load_config_file(%r)" % self.spec)
        global root_section
    
        self.config_path = resolve_package_config(self.spec)
    
        if self.config_path and self.config_path.exists and self.config_path.isfile:
            debug("loading %r config file" % self.config_path)
            (t1, t2) = self.config_path.splitext()
            if self.spec.version:
                self.actual_spec = self.spec
            else:
                self.actual_spec = PackageSpec(t1.basename)
            opts = Options(options)
            opts.pkg_spec    = self.spec.spec
            opts.pkg_name    = self.actual_spec.name
            opts.pkg_version = self.actual_spec.version
            opts.pkg_major   = self.actual_spec.major
            opts.pkg_minor   = self.actual_spec.minor
            opts.pkg_micro   = self.actual_spec.micro
            opts.pkg_extra   = self.actual_spec.extraversion
            cparser = IncludeConfigParser(self.config_path, opts=opts, root=root_section,
                                          base_include_dir=options.sysbuilder.package_config_dir)
            pkgconfig = cparser.parse()
            assert isinstance(pkgconfig, ConfigSection)
            self.config_section = pkgconfig

            self.needs = self.config_section.get('depends', None)
            if self.needs:
                self.needs = _str_to_list(self.needs)
            return True
        else:
            error("config file for %s not found" % self.spec)
        error("unknown error")
        return False

    def __copy__(self):
        return PackageConfig(packagespec=self)

def url2filename(url):
    return url.split('/')[-1]

def simple_download(dstdir, url, md5=None):
    import urllib2

    dstdir = Path(dstdir)
    filename = url2filename(url)
    try:
        u = urllib2.urlopen(url)
    except urllib2.URLError, exc:
        warn("connecting to %r: %s" % (url, exc))
        return False
    dstpathname = dstdir / Path(filename)
    assert isinstance(dstpathname, Path)
    f = open(dstpathname.pathname, 'wb')
    meta = u.info()
    filesize = int(meta.getheaders("Content-Length")[0])
    info("Downloading: %r from %r (size: %s)" % (dstpathname, url, humanize_filesize(filesize)))

    def print_status(downloaded, filesize):
        status = r"%10d  [%3.2f%%]" % (downloaded, downloaded * 100.0 / filesize)
        #status = status + chr(8)*(len(status)+1)
        #print status,
        info(status)
        
    downloaded = 0
    blocksize = 65536
    feedback_every_size = 1024*1024
    n_blocks    = (filesize + blocksize - 1) / blocksize
    feedback_every_blocks = (feedback_every_size + blocksize - 1) / blocksize
    n_feedbacks = n_blocks / feedback_every_blocks
    if n_feedbacks > 200:
        n_feedbacks = 200
        feedback_every_blocks = n_blocks / 200
    n_block = 0
    feedback_block = -1
    while True:
        if (n_block % feedback_every_blocks) == 0:
            print_status(downloaded, filesize)
            feedback_block = n_block
        try:
            block = u.read(blocksize)
        except Exception, exc:
            warn("receiving from %r: %s" % (url, exc))
            return False
        if not block:
            break
        downloaded += len(block)
        f.write(block)
        n_block += 1
    if feedback_block != n_block:
        print_status(downloaded, filesize)
    f.close()
    info("Download of %r completed." % dstpathname)
    if md5 is not None:
        md5_dl = md5_file(dstpathname.pathname)
        if md5_dl == md5:
            info("MD5 checksum OK for %s" % dstpathname)
        else:
            dstpathname.remove()
            error("MD5 check failed for %s (got:%r expected:%r). Deleting the file." % (dstpathname, md5_dl, md5))
            return False
    return dstpathname

def mirror_download(dstdir, url, mirrors, md5=None):
    debug("mirror_download(%r, %r, %r)" % (dstdir, url, mirrors))
    from urlparse import urljoin

    filename = url2filename(url)
    full_url = '://' in url

    if mirrors:
        n_mirrors = len(mirrors)
        for i in range(0, n_mirrors):
            mirror = mirrors[i]
            if not mirror.endswith('/'):
                mirror += '/'
            m_url = urljoin(mirror, filename)
            r = simple_download(dstdir, m_url, md5=md5)
            if r:
                return r
            if i + 1 < n_mirrors:
                warn("failed downloading %r from %r. Trying %r" % (filename, mirror, mirrors[i+1]))
            else:
                if full_url:
                    warn("failed downloading %r from %r. Trying original url %r" % (filename, mirror, url))
                else:
                    warn("failed downloading %r from %r. No more mirrors to try." % (filename, mirror))
    if full_url:
        r = simple_download(dstdir, url, md5=md5)
        if r:
            return r
    error("DOWNLOAD OF %r (%r) FAILED." % (filename, url))
    return False

def cached_download(dstdir, url, mirrors=None, cache_dir=None, md5=None):
    debug("cached_download(%r, %r, %r, %r)" % (dstdir, url, mirrors, cache_dir))
    filename = url2filename(url)
    dst_path = Path(dstdir) / filename
    if cache_dir is None:
        return mirror_download(dstdir, url, mirrors, md5=md5)
    assert cache_dir is not None
    cached_path = Path(cache_dir) / filename
    assert isinstance(cached_path, Path)
    if cached_path.exists:
        info("using already downloaded %s for %s" % (cached_path, url))
    else:
        if not mirror_download(dstdir, url, mirrors, md5=md5):
            return False
    assert cached_path.exists
    if not cached_path.same(dst_path):
        cached_path.copy(dst_path)
    return dst_path

# ========================================================================
#
#   Task support functions
#
# ========================================================================

def _load_target_config(target=None):
    """
    Load the embedded systems configuration file for the specified ``target``.
    """
    target = target or DEFAULT_TARGET_NAME

    options.sysbuilder.target     = target
    options.sysbuilder.target_dir = Path(options.sysbuilder.targets_dir) / target
    options.sysbuilder.build_dir  = Path(options.sysbuilder.target_dir) / 'build'
    options.sysbuilder.package_binary_dir = Path(options.sysbuilder.package_binary_base) / target
    options.sysbuilder.config = None

    opts = Options(options)
    opts.target = target

    base_dir = options.sysbuilder.system_config_dir
    if target != DEFAULT_TARGET_NAME:
        system_config_path = Path(base_dir) / ("system-%s.conf" % target)
    else:
        system_config_path = Path(base_dir) / "system.conf"
    cparser = IncludeConfigParser(system_config_path.pathname,
                                  opts=opts, root=root_section,
                                  base_include_dir=base_dir)
    sys_config = cparser.parse()
    sys_config.packages = _str_to_list(sys_config.packages)
    sys_config.native_packages = _str_to_list(sys_config.native_packages)

    options.sysbuilder.config          = sys_config
    options.sysbuilder.packages        = sys_config.packages
    options.sysbuilder.native_packages = sys_config.native_packages
    options.sysbuilder.kernel_config   = sys_config.kernel_config

    Path(options.sysbuilder.build_dir).makedirs()
    Path(options.sysbuilder.package_binary_dir).makedirs()

    return sys_config

def _package_download(packagespec, mirrors=None):
    debug("_package_download(%s)" % packagespec)
    pkgconfig = PackageConfig.Get(packagespec)
    info("Downloading package %s" % pkgconfig.spec)
    debug("Downloading package %s (actual:%s v:%s %s)" % (pkgconfig.spec, pkgconfig.actual_spec, pkgconfig.actual_spec.version, repr(pkgconfig)))

    if pkgconfig.config_section is None:
        error("can't find config file for %s package" % pkgconfig.spec)
    pkg_url     = pkgconfig.config_section.url
    pkg_mirrors = pkgconfig.config_section.get('mirrors', None)
    pkg_md5     = pkgconfig.config_section.get('md5', None)

    mirrors = mirrors or pkg_mirrors or options.sysbuilder.package_mirrors

    cache_dir = options.sysbuilder.package_dir
    return cached_download(dstdir=cache_dir,
                           url=pkg_url,
                           mirrors=mirrors, cache_dir=cache_dir,
                           md5=pkg_md5)

def _package_expand(packagespec, mirrors=None, removeexisting=True):
    debug("_package_expand(%s)" % packagespec)
    pkgconfig = PackageConfig.Get(packagespec)
    p = _package_download(pkgconfig, mirrors=mirrors)
    if p:
        info("Expanding package %s" % pkgconfig.spec)
        build_dir = options.sysbuilder.build_dir
        assert build_dir
        build_dir = Path(build_dir)
        assert isinstance(build_dir, Path)
        build_dir.makedirs()
        assert build_dir.exists and build_dir.isdir
        srcdir = pkgconfig.package_source_directory
        if srcdir.exists and removeexisting:
            info("Removing existing source directory %s." % srcdir)
            srcdir.nuke()
        if not srcdir.exists:
            info("Going to extract %s to %s" % (p, build_dir))
            p.uncompress(destdir=build_dir)
        if not srcdir.exists:
            error("package '%s' extraction didn't create the expected directory '%s'." % (pkgconfig.spec, srcdir))
            return None
        return srcdir
    return None

def _package_configure(packagespec, args):
    debug("_package_configure(%s)" % packagespec)
    pkgconfig = PackageConfig.Get(packagespec)
    srcdir = pkgconfig.package_source_directory
    if not srcdir.exists:
        srcdir = _package_expand(pkgconfig)
    if (not srcdir) or (not srcdir.exists) or (not srcdir.isdir):
        error("expected source directory '%s' doesn't exist or is of incorrect type." % srcdir)
        return False
    assert srcdir and srcdir.exists and srcdir.isdir
    olddir = cd(srcdir)
    cmdline = './configure %s' % args
    sh(cmdline)
    cd(olddir)
    return True

def _package_compile(packagespec):
    debug("_package_compile(%s)" % packagespec)
    pkgconfig = PackageConfig.Get(packagespec)
    if pkgconfig.built:
        info("package %s has already been built. Skipping build..." % packagespec)
        return True

    debug("package %s needs:%r" % (pkgconfig, pkgconfig.needs))
    if pkgconfig.needs:
        for n_pkgspec in pkgconfig.needs:
            n_pkgconfig = PackageConfig.Get(n_pkgspec)
            if n_pkgconfig.installed:
                continue
            if n_pkgconfig.built:
                info("Package %s is needed by %s, requesting install." % (n_pkgconfig, pkgconfig))
                _package_install(n_pkgconfig)
                continue
            info("Package %s is needed by %s, requesting build." % (n_pkgconfig, pkgconfig))
            _package_compile(n_pkgconfig)
            info("Package %s is needed by %s, requesting install." % (n_pkgconfig, pkgconfig))
            _package_install(n_pkgconfig)

    _package_expand(pkgconfig)
    srcdir = pkgconfig.package_source_directory
    #if not srcdir.exists:
    #    srcdir = _package_expand(pkgconfig)
    if (not srcdir) or (not srcdir.exists) or (not srcdir.isdir):
        error("expected source directory '%s' doesn't exist or is of incorrect type." % srcdir)
        return False
    assert srcdir and srcdir.exists and srcdir.isdir

    if (not pkgconfig.native) and (pkgconfig.actual_spec.name != 'uclibc'):
        _setup_target_build_environment()
    else:
        _clean_target_build_environment()

    olddir = cd(srcdir)

    # apply patches
    for patch_dir in (pkgconfig.config_path.dirname / ("patches-%s" % pkgconfig.actual_spec.version),
                      pkgconfig.config_path.dirname / "patches",):
        assert isinstance(patch_dir, Path)
        if not patch_dir.exists:
            continue
        assert patch_dir.exists
        info("applying patches to %s from %s" % (srcdir, patch_dir))
        for patch_file in sorted(Path(patch_dir / "*.patch").glob()):
            info("applying patch %s" % patch_file)
            sh("patch -Np1 -i %s" % patch_file)
        # if we've found a patch directory, then don't scan for lower priority ones
        break

    if pkgconfig.actual_spec.name == 'kernel':
        kernel_config_dir = pkgconfig.config_path.dirname / ("configs-%s" % pkgconfig.actual_spec.version)
        kernel_config = kernel_config_dir / options.sysbuilder.kernel_config
        info("Using kernel configuration file '%s'" % kernel_config)
        kernel_config.copy(srcdir / '.config')
        pkgconfig.config_section['KERNEL_CONFIG'] = kernel_config.pathname

    compile_cmd = pkgconfig.config_section.get('compile', None)
    if compile_cmd:
        sh(compile_cmd, ign_errors=False)
    else:
        cd(olddir)
        error("no compile instructions found for %s" % pkgconfig)
        return False

    destdir = srcdir / 'D'
    if destdir.exists:
        destdir.nuke()
    destdir.makedirs()

    cd(srcdir)
    pkgconfig.config_section['DESTDIR'] = destdir.pathname
    install_cmd = pkgconfig.config_section.get('install', None)
    debug("INSTALL_CMD:%r" % install_cmd)
    if install_cmd:
        sh(install_cmd)
    else:
        cd(olddir)
        error("no install instructions found for %s" % pkgconfig)
        return False

    cd(destdir)
    opts = Options(options)
    opts.binpkg = pkgconfig.package_binary_tarball
    sh('tar cpjf ${binpkg} .', opts=opts)

    cd(olddir)
    pkgconfig.built = True
    return True

def _package_install(packagespec):
    debug("_package_install(%s)" % packagespec)
    pkgconfig = PackageConfig.Get(packagespec)
    if pkgconfig.installed:
        info("package %s has already been installed. Skipping install..." % packagespec)
        return True

    debug("package %s needs:%r" % (pkgconfig, pkgconfig.needs))
    if pkgconfig.needs:
        for n_pkgspec in pkgconfig.needs:
            n_pkgconfig = PackageConfig.Get(n_pkgspec)
            if n_pkgconfig.installed:
                continue
            if n_pkgconfig.built:
                info("Package %s is needed by %s, requesting install." % (n_pkgconfig, pkgconfig))
                _package_install(n_pkgconfig)
                continue
            info("Package %s is needed by %s, requesting build." % (n_pkgconfig, pkgconfig))
            _package_compile(n_pkgconfig)
            info("Package %s is needed by %s, requesting install." % (n_pkgconfig, pkgconfig))
            _package_install(n_pkgconfig)

    if not pkgconfig.package_binary_tarball.exists:
        _package_compile(pkgconfig)

    if not pkgconfig.package_binary_tarball.exists:
        error("can't obtain binary package for %s" % pkgconfig)
        return False
    assert pkgconfig.package_binary_tarball.exists

    if pkgconfig.native:
        olddir = cd("/")
    else:
        olddir = cd(options.sysbuilder.target_dir)
    opts = Options(options)
    opts.binpkg = pkgconfig.package_binary_tarball
    sh('tar xpjf ${binpkg}', opts=opts)
    cd(olddir)
    pkgconfig.installed = True
    return True

_env_set = False
_env_build_set = False
_env_target_build_set = False

def _setup_environment():
    """
    Setup environment variables for CLFS build.
    """
    global _env_set
    if _env_set:
        return
    clfs_root = Path(options.sysbuilder.target_dir)

    CLFS   = clfs_root.pathname
    LC_ALL = "POSIX"
    PATH   = "%s:%s" % (clfs_root / 'cross-tools' / 'bin', os.environ['PATH'])

    os.environ['CLFS']   = CLFS
    os.environ['LC_ALL'] = LC_ALL
    os.environ['PATH']   = PATH

    options.sysbuilder.CLFS   = CLFS
    options.sysbuilder.LC_ALL = LC_ALL
    options.sysbuilder.PATH   = PATH

    options.CLFS = options.sysbuilder.CLFS

    _env_set = True

def _get_shell_variable(varname):
    import subprocess
    p = subprocess.Popen(["/bin/bash", "-c", "echo $%s" % varname], stdout=subprocess.PIPE, shell=False)
    (out, err) = p.communicate()
    if out.endswith('\n'):
        out = out[:-1]
    return out

def _setup_build_environment():
    global _env_build_set
    if _env_build_set:
        return
    _setup_environment()
    to_unset = ('CFLAGS', 'CXXFLAGS',)
    for var in to_unset:
        if var in os.environ:
            del os.environ[var]
    machtype = _get_shell_variable('MACHTYPE')
    hosttype = _get_shell_variable('HOSTTYPE')

    import re

    target_sys_name = TARGET_SYS_NAME
    target_sys      = TARGETS[target_sys_name]
    target_triplet  = target_sys['triplet']
    target_cpu      = target_sys['compiler_cpu']
    target_arch     = re.sub(r'i.86', 'i386',
                             re.sub(r'-.*', '', target_triplet))
    target_endian   = target_sys['endian']
    host = re.sub(r'-[^-]*', '-cross', machtype, 1)

    os.environ['MACHTYPE']    = machtype
    os.environ['HOSTTYPE']    = hosttype
    os.environ['CLFS_HOST']   = host
    os.environ['CLFS_TARGET'] = target_triplet
    os.environ['CLFS_ARCH']   = target_arch
    os.environ['CLFS_ENDIAN'] = target_endian
    os.environ['CLFS_CPU']    = target_cpu

    options.sysbuilder.MACHTYPE    = machtype
    options.sysbuilder.HOSTTYPE    = hosttype
    options.sysbuilder.CLFS_HOST   = host
    options.sysbuilder.CLFS_TARGET = target_triplet
    options.sysbuilder.CLFS_ARCH   = target_arch
    options.sysbuilder.CLFS_ENDIAN = target_endian
    options.sysbuilder.CLFS_CPU    = target_cpu

    options.MACHTYPE    = options.sysbuilder.MACHTYPE
    options.HOSTTYPE    = options.sysbuilder.HOSTTYPE
    options.CLFS_HOST   = options.sysbuilder.CLFS_HOST
    options.CLFS_TARGET = options.sysbuilder.CLFS_TARGET
    options.CLFS_ARCH   = options.sysbuilder.CLFS_ARCH
    options.CLFS_ENDIAN = options.sysbuilder.CLFS_ENDIAN
    options.CLFS_CPU    = options.sysbuilder.CLFS_CPU

    info("HOST:%r TARGET:%r ARCH:%r CPU:%r ENDIAN:%r" % (options.CLFS_HOST, options.CLFS_TARGET, options.CLFS_ARCH, options.CLFS_CPU, options.CLFS_ENDIAN))
    _env_build_set = True

def _setup_target_build_environment():
    global _env_target_build_set
    if _env_target_build_set:
        return
    _setup_build_environment()

    target_sys_name = TARGET_SYS_NAME
    target_sys      = TARGETS[target_sys_name]
    target_triplet  = target_sys['triplet']

    cc      = "%s-gcc" % target_triplet
    cxx     = "%s-g++" % target_triplet
    ar      = "%s-ar" % target_triplet
    _as     = "%s-as" % target_triplet
    ld      = "%s-ld" % target_triplet
    ranlib  = "%s-ranlib" % target_triplet
    readelf = "%s-readelf" % target_triplet
    strip   = "%s-strip" % target_triplet

    os.environ['CC']      = cc
    os.environ['CXX']     = cxx
    os.environ['AR']      = ar
    os.environ['AS']      = _as
    os.environ['LD']      = ld
    os.environ['RANLIB']  = ranlib
    os.environ['READELF'] = readelf
    os.environ['STRIP']   = strip

    options.sysbuilder.CC      = cc
    options.sysbuilder.CXX     = cxx
    options.sysbuilder.AR      = ar
    options.sysbuilder.AS      = _as
    options.sysbuilder.LD      = ld
    options.sysbuilder.RANLIB  = ranlib
    options.sysbuilder.READELF = readelf
    options.sysbuilder.STRIP   = strip

    options.CC      = cc
    options.CXX     = cxx
    options.AR      = ar
    options.AS      = _as
    options.LD      = ld
    options.RANLIB  = ranlib
    options.READELF = readelf
    options.STRIP   = strip

    _env_target_build_set = True

def _clean_target_build_environment():
    global _env_target_build_set
    if not _env_target_build_set:
        return
    del os.environ['CC']
    del os.environ['CXX']
    del os.environ['AR']
    del os.environ['AS']
    del os.environ['LD']
    del os.environ['RANLIB']
    del os.environ['READELF']
    del os.environ['STRIP']
    options.sysbuilder.CC      = ""
    options.sysbuilder.CXX     = ""
    options.sysbuilder.AR      = ""
    options.sysbuilder.AS      = ""
    options.sysbuilder.LD      = ""
    options.sysbuilder.RANLIB  = ""
    options.sysbuilder.READELF = ""
    options.sysbuilder.STRIP   = ""
    options.CC      = ""
    options.CXX     = ""
    options.AR      = ""
    options.AS      = ""
    options.LD      = ""
    options.RANLIB  = ""
    options.READELF = ""
    options.STRIP   = ""
    _env_target_build_set = False


# ========================================================================
#
#   Tasks
#
# ========================================================================

# ------------------------------------------------------------------------
#   SYSTEM TASKS
# ------------------------------------------------------------------------

@task
@cmdline([
    ('target=', 't', None, "target system name"),
    ('package=', 'p', None, "DUMMY"),
], propagate=True)
def load_target_config(ctxt):
    assert isinstance(ctxt, TaskContext)
    sys_config = _load_target_config(ctxt.cmdline_opts.target)
    _setup_build_environment()

@task
@cmdline([
    ('target=', 't', None, "target system name")
])
@depends('load_target_config')
def clean(ctxt):
    """
    Clean the whole embedded system's tree and sources.
    """
    assert isinstance(ctxt, TaskContext)
    sys_config = options.sysbuilder.config
    clfs_root = Path(options.sysbuilder.target_dir)
    clfs_root.nuke()
    PackageConfig._db_remove()

@task
@cmdline([
    ('target=', 't', None, "target system name")
], propagate=True)
@depends('load_target_config', 'create_tree')
def create(ctxt):
    """
    Assemble the embedded system's tree.
    """
    assert isinstance(ctxt, TaskContext)
    sys_config = options.sysbuilder.config
    for packagespec in options.sysbuilder.native_packages:
        call_task('package_install', cmdline=['--package', packagespec])
    for packagespec in options.sysbuilder.packages:
        call_task('package_install', cmdline=['--package', packagespec])

def _create_tree():
    clfs_root = Path(options.sysbuilder.target_dir)
    
    clfs_root.makedirs()
    for c in ('bin', 'sbin', 'boot', 'dev', 'etc', 'etc/opt', 'opt', 'home',
              'lib', 'lib/firmware', 'lib/modules', 'mnt',
              'proc', 'media', 'root', 'srv', 'sys', 'tmp', 'usr', 'var',):
        p = clfs_root / c
        p.makedirs()
    for c in ('lock', 'log', 'mail', 'run', 'spool', 'opt', 'cache', 'lib', 'lib/misc', 'lib/locate', 'local', 'tmp',):
        p = clfs_root / 'var' / c
        p.makedirs()
    for c in ('bin', 'include', 'lib', 'sbin', 'src',):
        p = clfs_root / 'usr' / c
        p.makedirs()
        p = clfs_root / 'usr' / 'local' / c
        p.makedirs()
    for c in ('doc', 'info', 'locale', 'man', 'misc', 'terminfo', 'zoneinfo',):
        p = clfs_root / 'usr' / 'share' / c
        p.makedirs()
        p = clfs_root / 'usr' / 'local' / 'share' / c
        p.makedirs()
    for c in range(1, 9):
        p = clfs_root / 'usr' / 'share' / 'man' / ("man%s" % c)
        p.makedirs()
        p = clfs_root / 'usr' / 'local' / 'share' / 'man' / ("man%s" % c)
        p.makedirs()
    for c in ('man', 'doc', 'info',):
        p = Path('share') / c
        for d in (clfs_root / 'usr' / c, clfs_root / 'usr' / 'local' / c):
            if not d.exists:
                p.symlink(d)
    sh("install -dv -m 0750 %s" % (clfs_root / 'root'))
    sh("install -dv -m 1777 %s" % (clfs_root / 'tmp'))
    sh("install -dv -m 1777 %s" % (clfs_root / 'var' / 'tmp'))

    import stat
    for p, mode, major, minor in ((Path(clfs_root / 'dev' / 'null'), 0666 | stat.S_IFCHR, 1, 3),
                    (Path(clfs_root / 'dev' / 'console'), 0600 | stat.S_IFCHR, 5, 1)):
        if not p.exists:
            p.mknod(mode, major, minor)

    for root, dirs, files in clfs_root.walk():
        root.chown(0, 0)
    #Path(clfs_root / 'var' / 'run' / 'utmp').chgrp(13) # utmp
    #Path(clfs_root / 'var' / 'log' / 'lastlog').chgrp(13) # utmp

    Path(clfs_root / 'cross-tools' / 'bin').makedirs()

@task
@depends('load_target_config')
def create_tree(ctxt):
    """Create the base embedded system directory tree."""
    assert isinstance(ctxt, TaskContext)
    _create_tree()

@task
@cmdline([
    ('target=', 't', None, "target system name")
])
@depends('load_target_config')
def mkimage(ctxt):
    """
    Build a disk image with the embedded system's tree.
    """
    assert isinstance(ctxt, TaskContext)
    sys_config = options.sysbuilder.config
    raise "TODO"

# ------------------------------------------------------------------------
#   PACKAGE TASKS
# ------------------------------------------------------------------------

@task
@cmdline([
    ('package=', 'p', None, "package specifier for the package to download")
])
@depends('load_target_config')
def package_download(ctxt):
    """
    Download the specified package to the package cache directory
    (as specified in options.sysbuilder.package_dir).
    """
    assert isinstance(ctxt, TaskContext)
    packagespec = ctxt.cmdline_opts.package
    _package_download(packagespec)

@task
@cmdline([
    ('package=', 'p', None, "package specifier for the package to expand")
])
@depends('load_target_config')
def package_expand(ctxt):
    """
    Expand the specified package to the build directory
    (as specified in options.sysbuilder.build_dir).

    If not present in the package cache, the package is downloaded.
    """
    assert isinstance(ctxt, TaskContext)
    packagespec = ctxt.cmdline_opts.package
    _package_expand(packagespec)

@task
@cmdline([
    ('package=', 'p', None, "package specifier for the package to expand")
])
@depends('load_target_config')
def package_install(ctxt):
    """
    Install the specified package into the target system.

    If the binary package is not available, it's compiled.
    """
    assert isinstance(ctxt, TaskContext)
    packagespec = ctxt.cmdline_opts.package
    _package_install(packagespec)

@task
@cmdline([
    ('target=', 't', None, "target system name"),
    ('package=', 'p', None, "package specifier"),
], propagate=True)
@depends('load_target_config')
def package_status(ctxt):
    """
    Report the status about the specified package (or all the built/installed
    packages if one is not specified).
    """
    assert isinstance(ctxt, TaskContext)
    packagespec = ctxt.cmdline_opts.package
    packages = []
    PackageConfig._db_init()
    if packagespec:
        packages = [PackageConfig.Get(packagespec)]
    else:
        packages = PackageConfig.DB_Packages()
    def bool2str(value):
        if value in (True, 1, "1", "true", "t", "yes", "y"):
            return "yes"
        return "no"
    FMT_STRING = "%-20s %-10s %-5s %-5s %-5s %-5s %-50s"
    header = FMT_STRING % ("name", "vers.", "ok", "built", "inst.", "n.ve", "needs")
    separator = "-" * len(header)
    info(header)
    info(separator)
    for pkgconfig in packages:
        assert isinstance(pkgconfig, PackageConfig)
        needs = "--"
        if pkgconfig.needs:
            needs = ",".join(pkgconfig.needs)
        needs = needs[:50]
        name  = "%s" % pkgconfig.actual_spec.name
        version = "%s" % pkgconfig.actual_spec.version
        status = FMT_STRING % (name[:20], version[:10],
                               bool2str(pkgconfig.ok), bool2str(pkgconfig.built), bool2str(pkgconfig.installed),
                               bool2str(pkgconfig.native), needs)
        info(status)

@task
@cmdline([
    ('target=', 't', None, "target system name"),
    ('package=', 'p', None, "package specifier"),
    ('status=', 's', None, "forse package status (+: enable, -: disable, i: installed; b: built)"),
], propagate=True)
@depends('load_target_config')
def package_force(ctxt):
    """
    Force the status for the specified package.
    """
    assert isinstance(ctxt, TaskContext)
    packagespec = ctxt.cmdline_opts.package
    pkgconfig = PackageConfig.Get(packagespec)
    assert isinstance(pkgconfig, PackageConfig)
    status = ctxt.cmdline_opts.status
    on = True
    for ch in status:
        if ch == '+':
            on = True
        elif ch == '-':
            on = False
        elif ch == 'i':
            pkgconfig.installed = on
        elif ch == 'b':
            pkgconfig.built = on
    pkgconfig._db_save()

@task
@cmdline([
    ('target=', 't', None, "target system name"),
    ('package=', 'p', None, "package specifier"),
], propagate=True)
@depends('load_target_config')
def package_clean(ctxt):
    """
    Mark the package as not built and not installed. Remove the compiled tarball.
    """
    assert isinstance(ctxt, TaskContext)
    packagespec = ctxt.cmdline_opts.package
    pkgconfig = PackageConfig.Get(packagespec)
    assert isinstance(pkgconfig, PackageConfig)
    if pkgconfig.package_binary_tarball.exists:
        pkgconfig.package_binary_tarball.nuke()
    if pkgconfig.package_source_directory.exists:
        pkgconfig.package_source_directory.nuke()
    pkgconfig.installed = False
    pkgconfig.built = False
    pkgconfig._db_save()
