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

from automa.opts import options
from automa.tasks import TaskContext
from automa.path import Path
from automa.shell import sh
from automa.configfile import ConfigParser, IncludeConfigParser, ConfigAction, ConfigSection
from automa.utils import *
from automa.log import *

def url2filename(url):
    return url.split('/')[-1]

def simple_download(dstdir, url):
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

    downloaded = 0
    blocksize = 65536
    feedback_every_size = 1024*1024
    n_feedbacks = filesize / feedback_every_size
    n_blocks    = (filesize + blocksize - 1) / blocksize
    feedback_every_blocks = n_blocks / n_feedbacks
    n_block = 0
    while True:
        try:
            block = u.read(blocksize)
        except Exception, exc:
            warn("receiving from %r: %s" % (url, exc))
            return False
        if not block:
            break
        downloaded += len(block)
        f.write(block)
        if (n_block % feedback_every_blocks) == 0:
            status = r"%10d  [%3.2f%%]" % (downloaded, downloaded * 100.0 / file_size)
            #status = status + chr(8)*(len(status)+1)
            #print status,
            info(status)
        n_block += 1
    f.close()
    info("Download of %r completed." % dstpathname)
    return True

def mirror_download(dstdir, url, mirrors):
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
            if simple_download(dstdir, m_url):
                return True
            if i + 1 < n_mirrors:
                warn("failed downloading %r from %r. Trying %r" % (filename, mirror, mirrors[i+1]))
            else:
                if full_url:
                    warn("failed downloading %r from %r. Trying original url %r" % (filename, mirror, url))
                else:
                    warn("failed downloading %r from %r. No more mirrors to try." % (filename, mirror))
    if full_url:
        if simple_download(dstdir, url):
            return True
    error("DOWNLOAD OF %r (%r) FAILED." % (filename, url))
    return False

def cached_download(dstdir, url, mirrors=None, cache_dir=None):
    filename = url2filename(url)
    dst_path = Path(dstdir) / filename
    if cache_dir is None:
        return mirror_download(dstdir, url, mirrors)
    assert cache_dir is not None
    cached_path = Path(cache_dir) / filename
    assert isinstance(cached_path, Path)
    if not cached_path.exists:
        if not mirror_download(dstdir, url, mirrors):
            return False
    assert cached_path.exists
    if not cached_path.same(dst_path):
        cached_path.copy(dst_path)
    return True

PACKAGESPEC_VERSION_RE = re.compile(r'^([a-zA-Z0-9-]+)-([0-9\.]+)')

class PackageSpec(object):
    """
    A package specification.
    It comprises a ``name`` and a ``version``.
    The ``version`` can be left unspecified, thus being None.
    """
    def __init__(self, packagespec=None, name=None, version=None):
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
                self.name = packagespec.name
                self.version = packagespec.version
            elif isinstance(packagespec, basestring):
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
        return self

class PackageConfigParser(ConfigParser):
    """
    automa.sysbuilder ConfigParser

    It is used to load package configuration files.
    It that handles 'include' actions.
    """

    def resolve_include_path(self, includepath):
        from automa.utils import _is_iterable
        includepath_obj = Path(includepath)
        if includepath_obj.isabs:
            return includepath
        base_include_dir = options.sysbuilder.package_config_dir
        if _is_iterable(base_include_dir):
            for base_dir in base_include_dir:
                includepath_obj = Path(base_dir) / includepath
                if includepath_obj.exists:
                    return includepath_obj.pathname
        else:
            includepath_obj = Path(base_include_dir) / includepath
            return includepath_obj.pathname
        return includepath

    def handle_include(self, entry):
        assert isinstance(entry, ConfigAction)
        pathname = self.resolve_include_path(entry.value)
        cparser = PackageConfigParser(pathname, opts=self.opts, root=self.root)
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
    if not _is_iterable(base_pkgconfig_dir):
        base_pkgconfig_dir = [base_pkgconfig_dir]

    for pkgconfig_dir in base_pkgconfig_dir:
        if pspec.version:
            pkgconfig_v_glob = Path(pkgconfig_dir) / ("%s/%s-%s.config" % (pspec.name, pspec.name, pspec.version))
            pkgconfig_glob = Path(pkgconfig_dir) / ("%s/%s.config" % (pspec.name, pspec.name))
            all_pkgconfig_objs = pkgconfig_v_glob.glob() + pkgconfig_glob.glob()
        else:
            pkgconfig_v_glob = Path(pkgconfig_dir) / ("%s/%s-*.config" % (pspec.name, pspec.name))
            pkgconfig_glob = Path(pkgconfig_dir) / ("%s/%s.config" % (pspec.name, pspec.name))
            all_pkgconfig_objs = pkgconfig_v_glob.glob() + pkgconfig_glob.glob()
        highest_version = None
        highest_pkgconfig = None
        for pkgconfig_obj in all_pkgconfig_objs:
            if pkgconfig_obj.exists:
                (t1, t2) = pkgconfig_obj.splitext()
                spec = PackageSpec(t1.pathname)
                if (highest_version is None) or (spec.version_number > highest_version):
                    highest_version = spec.version_number
                    highest_pkgconfig = pkgconfig_obj
        if highest_pkgconfig and highest_pkgconfig.exists:
            return highest_pkgconfig
    return None

root_section = None

def load_package_configfile(packagespec):
    """
    Load the proper config file for the package described by ``packagespec``,
    if such a file exists, and return the correspoding configfile.ConfigSection

    Otherwise return None.
    """
    global root_section

    config_path = resolve_package_config(packagespec)

    if config_path and config_path.exists and config_path.isfile:
        cparser = PackageConfigParser(config_path, opts=options, root=root_section)
        pkgconfig = cparser.parse()
        assert isinstance(pkgconfig, ConfigSection)
        return pkgconfig
    return None

def package_download(package, mirrors=None):
    mirrors = mirrors or options.sysbuilder.package_mirrors
    package_filename = Path(package).basename

    assert False, "handle package config loading"

    cache_dir = options.sysbuilder.package_dir
    return cached_download(dstdir=cache_dir,
                           url=package,
                           mirrors=mirrors, cache_dir=cache_dir)
