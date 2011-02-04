# Download and install mx.ODBC, plus it's license file
# Note: Windows is not supported by this recipe

import logging
import os
import platform
import shutil
import sys
import tempfile
import urllib2
import urlparse

import setuptools.archive_util
import zc.buildout

# mx.ODBC version
VERSION = '3.0.4'

BASE_URL = 'http://downloads.egenix.com/python/egenix-mxodbc-' + VERSION + '.'
EXTENSION = '.prebuilt.zip'

MXBASE_URL = 'http://downloads.egenix.com/python/egenix-mx-base-3.0.0.zip'

# Keyed on .python_version_tuple()[:2] + (.system(), .machine())
# (methods from the platform module, python version tuple as ints)
# not all of these have been tested
_urls = {
    # Linux 32bit
    (2, 1, 'Linux', 'i686'): 'linux-i686-py2.1',
    (2, 2, 'Linux', 'i686'): 'linux-i686-py2.2',
    (2, 3, 'Linux', 'i686'): 'linux-i686-py2.3',
    (2, 4, 'Linux', 'i686'): 'linux-i686-py2.4',
    (2, 5, 'Linux', 'i686'): 'linux-i686-py2.5',
    (2, 6, 'Linux', 'i686'): 'linux-i686-py2.6',
    
    # Linux 64bit
    (2, 1, 'Linux', 'x86_64'): 'linux-x86_64-py2.1',
    (2, 2, 'Linux', 'x86_64'): 'linux-x86_64-py2.2',
    (2, 3, 'Linux', 'x86_64'): 'linux-x86_64-py2.3',
    (2, 4, 'Linux', 'x86_64'): 'linux-x86_64-py2.4',
    (2, 5, 'Linux', 'x86_64'): 'linux-x86_64-py2.5',
    (2, 6, 'Linux', 'x86_64'): 'linux-x86_64-py2.6',
    
    # Mac OSX (fat binaries)
    (2, 3, 'Darwin', 'i386'): 'darwin-8.9.0-Power_Macintosh-py2.3',
    (2, 4, 'Darwin', 'i386'): 'macosx-10.4-ppc-py2.4',
    (2, 5, 'Darwin', 'i386'): 'macosx-10.4-fat-py2.5',
    (2, 6, 'Darwin', 'i386'): 'macosx-10.4-fat-py2.6',
    (2, 3, 'Darwin', 'Power Macintosh'): 'darwin-8.9.0-Power_Macintosh-py2.3',
    (2, 4, 'Darwin', 'Power Macintosh'): 'macosx-10.4-ppc-py2.4',
    (2, 5, 'Darwin', 'Power Macintosh'): 'macosx-10.4-fat-py2.5',
    (2, 6, 'Darwin', 'Power Macintosh'): 'macosx-10.4-fat-py2.6',
    
    # XXX Solaris and FreeBSD
}

# Unicode size
_ucs = (sys.maxunicode < 66000) and 'ucs2' or 'ucs4'

_key = tuple(map(int, platform.python_version_tuple()[:2])) + (
     platform.system(), platform.machine())
    
try:
    URL = '%s%s_%s%s' % (BASE_URL, _urls[_key], _ucs, EXTENSION)
except KeyError:
    # Cannot determine for this platform
    URL = ''

def system(c):
    if os.system(c):
        raise SystemError('Failed', c)

class Recipe(object):
    def __init__(self, buildout, name, options):
        self.logger = logging.getLogger(name)
        self.buildout = buildout
        self.name = name
        self.options = options
        
        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'], self.name)
            
        buildout['buildout'].setdefault(
            'download-directory',
            os.path.join(buildout['buildout']['directory'], 'downloads'))
        
        self.options.setdefault('url', URL)
        self.options.setdefault('licenses-archive', 'mxodbc-licenses.zip')
        self.options.setdefault('license-key', '')
    
    def install(self):
        location = self.options['location']
        if not os.path.exists(location):
            os.mkdir(location)
        
        self._install_mxbase(location)
        self._install_mxodbc(location)
        self._install_license(location)
        
        return [location]
    
    def update(self):
        pass
    
    def _install_mxbase(self, location):
        fname = self._download(MXBASE_URL)

        tmp = tempfile.mkdtemp('buildout-' + self.name)
        dirname = os.path.splitext(os.path.basename(fname))[0]
        package = os.path.join(tmp, dirname)
        here = os.getcwd()
        try:
            self.logger.debug('Extracting mx.Base archive')
            setuptools.archive_util.unpack_archive(fname, tmp)
            os.chdir(package)
            self.logger.debug('Installing mx.BASE into %s', location)
            system('"%s" setup.py -q install'
                   ' --install-purelib="%s" --install-platlib="%s"' % (
                        sys.executable, location, location))
        finally:
            os.chdir(here)
            shutil.rmtree(tmp)
    
    def _install_mxodbc(self, location):
        url = self.options['url']
        fname = self._download(url)
            
        tmp = tempfile.mkdtemp('buildout-' + self.name)
        basename = os.path.basename(fname)
        package = os.path.join(tmp, os.path.splitext(basename)[0])
        here = os.getcwd()
        try:
            self.logger.debug('Extracting mx.ODBC archive')
            setuptools.archive_util.unpack_archive(fname, tmp)
            os.chdir(package)
            self.logger.debug('Installing mx.ODBC into %s', location)
            system('"%s" setup.py -q build --skip install'
                   ' --install-purelib="%s" --install-platlib="%s"' % (
                        sys.executable, location, location))
        finally:
            os.chdir(here)
            shutil.rmtree(tmp)
    
    def _install_license(self, location):
        licenses_archive = os.path.join(
            self.buildout['buildout']['directory'], 
            self.options['licenses-archive'])
        license_key = self.options['license-key']
        dest = os.path.join(location, 'mx', 'ODBC')
        tmp = tempfile.mkdtemp('buildout-' + self.name)
        
        try:
            setuptools.archive_util.unpack_archive(licenses_archive, tmp)
            directories = [f for f in os.listdir(tmp)
                           if os.path.isdir(os.path.join(tmp, f))]
            license_key = license_key or directories[0]
            if not license_key in directories:
                raise zc.buildout.UserError(
                    "License key not found: %s" % license_key)

            self.logger.info('Installing mx.ODBC license %s', license_key)
            license_path = os.path.join(tmp, license_key)            
            shutil.copy(os.path.join(license_path, 'license.py'), dest)
            shutil.copy(os.path.join(license_path, 'license.txt'), dest)
        finally:
            shutil.rmtree(tmp)
    
    def _download(self, url):
        download_dir = self.buildout['buildout']['download-directory']
        if not os.path.isdir(download_dir):
            os.mkdir(download_dir)
            self.options.created(download_dir)
                
        urlpath = urlparse.urlparse(url)[2]
        fname = os.path.join(download_dir, urlpath.split('/')[-1])
        if not os.path.exists(fname):
            self.logger.info('Downloading ' + url)
            f = open(fname, 'wb')
            try:
                f.write(urllib2.urlopen(url).read())
            except Exception, e:
                os.remove(fname)
                raise zc.buildout.UserError(
                    "Failed to download URL %s: %s" % (url, str(e)))
            f.close()
            
        return fname
