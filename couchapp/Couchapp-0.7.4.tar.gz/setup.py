# -*- coding: utf-8 -*-
#
# This file is part of couchapp released under the Apache 2 license. 
# See the NOTICE for more information.

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import Extension


from distutils.core import Extension
from distutils.sysconfig import get_python_lib
from distutils.cmd import Command
from distutils.command.build import build
from distutils.command.install_data import install_data
import os
import sys

from couchapp import __version__

if not hasattr(sys, 'version_info') or sys.version_info < (2, 5, 0, 'final'):
    raise SystemExit("Couchapp requires Python 2.5 or later.")

executables = []
setup_requires = []
extra = {}

def get_data_files():
    data_files = []
    data_files.append(('couchapp', 
                       ["LICENSE", "MANIFEST.in", "NOTICE", "README.md", 
                        "THANKS.txt",]))
    return data_files

def ordinarypath(p):
    return p and p[0] != '.' and p[-1] != '~'

def get_packages_data():
    packagedata = {'couchapp': []}

    for root in ('templates',):
        for curdir, dirs, files in os.walk(os.path.join("couchapp", root)):
            print curdir
            curdir = curdir.split(os.sep, 1)[1]
            dirs[:] = filter(ordinarypath, dirs)
            for f in filter(ordinarypath, files):
                f = os.path.join(curdir, f)
                packagedata['couchapp'].append(f)
    return packagedata 

def all_packages():
    return [
        'couchapp',
        'couchapp.ext',
        'couchapp.hooks',
        'couchapp.hooks.compress',
        'couchapp.restkit',
        'couchapp.restkit.manager',
        'couchapp.restkit.contrib',
        'couchapp.simplejson',
        'couchapp.ssl',
        'couchapp.vendors',
        'couchapp.vendors.backends',
    ]

def get_scripts():
    scripts = [os.path.join("resources", "scripts", "couchapp")]
    if os.name == "nt":
        scripts.append(os.path.join("resources", "scripts",
            "couchapp.bat"))
    return scripts

if os.name == "nt" or sys.platform == "win32":
    # py2exe needs to be installed to work
    try:
        import py2exe

        # Help py2exe to find win32com.shell
        try:
            import modulefinder
            import win32com
            for p in win32com.__path__[1:]: # Take the path to win32comext
                modulefinder.AddPackagePath("win32com", p)
            pn = "win32com.shell"
            __import__(pn)
            m = sys.modules[pn]
            for p in m.__path__[1:]:
                modulefinder.AddPackagePath(pn, p)
        except ImportError:
            raise SystemExit('You need pywin32 installed ' +
                    'http://sourceforge.net/projects/pywin32')

        # If run without args, build executables, in quiet mode.
        if len(sys.argv) == 1:
            sys.argv.append("py2exe")
            sys.argv.append("-q")

        extra['console'] = [{
             'script': os.path.join("resources", "scripts", "couchapp"),
             'copyright':'Copyright (C) 2008-2011 Benoît Chesneau and others',
             'product_version': __version__ 
        }]


    except ImportError:
        raise SystemExit('You need py2exe installed to run Couchapp.')

class install_package_data(install_data):
    def finalize_options(self):
        self.set_undefined_options('install',
                                   ('install_lib', 'install_dir'))
        install_data.finalize_options(self)


# ssl build

def find_file(filename, std_dirs, paths):
    """Searches for the directory where a given file is located,
    and returns a possibly-empty list of additional directories, or None
    if the file couldn't be found at all.

    'filename' is the name of a file, such as readline.h or libcrypto.a.
    'std_dirs' is the list of standard system directories; if the
        file is found in one of them, no additional directives are needed.
    'paths' is a list of additional locations to check; if the file is
        found in one of them, the resulting list will contain the directory.
    """

    # Check the standard locations
    for dir in std_dirs:
        f = os.path.join(dir, filename)
        print 'looking for', f
        if os.path.exists(f): return []

    # Check the additional directories
    for dir in paths:
        f = os.path.join(dir, filename)
        print 'looking for', f
        if os.path.exists(f):
            return [dir]

    # Not found anywhere
    return None

def find_library_file(compiler, libname, std_dirs, paths):
    result = compiler.find_library_file(std_dirs + paths, libname)
    if result is None:
        return None

    # Check whether the found file is in one of the standard directories
    dirname = os.path.dirname(result)
    for p in std_dirs:
        # Ensure path doesn't end with path separator
        p = p.rstrip(os.sep)
        if p == dirname:
            return [ ]

    # Otherwise, it must have been in one of the additional directories,
    # so we have to figure out which one.
    for p in paths:
        # Ensure path doesn't end with path separator
        p = p.rstrip(os.sep)
        if p == dirname:
            return [p]
    else:
        assert False, "Internal error: Path not found in std_dirs or paths"


def find_ssl():

    # Detect SSL support for the socket module (via _ssl)
    from distutils.ccompiler import new_compiler

    compiler = new_compiler()
    inc_dirs = compiler.include_dirs + ['/usr/include']

    search_for_ssl_incs_in = [
                          '/usr/local/ssl/include',
                          '/usr/contrib/ssl/include/'
                         ]
    ssl_incs = find_file('openssl/ssl.h', inc_dirs,
                         search_for_ssl_incs_in
                         )
    if ssl_incs is not None:
        krb5_h = find_file('krb5.h', inc_dirs,
                           ['/usr/kerberos/include'])
        if krb5_h:
            ssl_incs += krb5_h

    ssl_libs = find_library_file(compiler, 'ssl',
                                 ['/usr/lib'],
                                 ['/usr/local/lib',
                                  '/usr/local/ssl/lib',
                                  '/usr/contrib/ssl/lib/'
                                 ] )

    if (ssl_incs is not None and ssl_libs is not None):
        return ssl_incs, ssl_libs, ['ssl', 'crypto']

    raise Exception("No SSL support found")


socket_inc = "./couchapp/ssl/2.5.1"


link_args = []
if sys.platform == 'win32':

    # Assume the openssl libraries from GnuWin32 are installed in the
    # following location:
    gnuwin32_dir = os.environ.get("GNUWIN32_DIR", r"C:\Utils\GnuWin32")

    # Set this to 1 for a dynamic build (depends on openssl DLLs)
    # Dynamic build is about 26k, static is 670k
    dynamic = int(os.environ.get("SSL_DYNAMIC", 0))

    ssl_incs = [os.environ.get("C_INCLUDE_DIR") or os.path.join(gnuwin32_dir, "include")]
    ssl_libs = [os.environ.get("C_LIB_DIR") or os.path.join(gnuwin32_dir, "lib")]
    libs = ['ssl', 'crypto', 'wsock32']
    if not dynamic:
	libs = libs + ['gdi32', 'gw32c', 'ole32', 'uuid']
        link_args = ['-static']
else:
    ssl_incs, ssl_libs, libs = find_ssl()

if sys.version_info < (2, 6, 0):
    extra['ext_modules']=[Extension('couchapp.ssl._ssl2', ['couchapp/ssl/_ssl2.c'],
                                 include_dirs = ssl_incs + [socket_inc],
                                 library_dirs = ssl_libs,
                                 libraries = libs,
                                 extra_link_args = link_args)]

cmdclass = {'install_data': install_package_data }
 
setup(
    name = 'Couchapp',
    version = __version__,
    url = 'http://github.com/couchapp/couchapp/tree/master',
    license =  'Apache License 2',
    author = 'Benoit Chesneau',
    author_email = 'benoitc@e-engura.org',
    description = 'Standalone CouchDB Application Development Made Simple.',
    long_description = """CouchApp is a set of helpers and a jQuery plugin
    that conspire to get you up and running on CouchDB quickly and
    correctly. It brings clarity and order to the freedom of CouchDB's
    document-based approach.""",
    keywords = 'couchdb couchapp',
    platforms = ['any'],
    classifiers = [
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Database',
        'Topic :: Utilities',
    ],

    packages = all_packages(),
    package_data = get_packages_data(),
    data_files=get_data_files(),

    cmdclass=cmdclass,

    scripts=get_scripts(),

    

    options = dict(py2exe={
                        'dll_excludes': [
                            "kernelbase.dll",
                            "powrprof.dll" 
                        ]
                   },

                   bdist_mpkg=dict(zipdist=True,
                                   license='LICENSE',
                                   readme='resources/macosx/Readme.html',
                                   welcome='resources/macosx/Welcome.html')
    ),
 
    **extra
)
