r"""
Introduction
---------------

ISAPIWSGIHelper is a small command line script and some helper
utilities to help bootstrap deployment of WSGI
applications using `isapi-wsgi <http://code.google.com/p/isapi-wsgi/>`_ with
Microsoft IIS.

Prerequisites
---------------

The following should be installed:

* Python
* Python Win32 Extensions

In addition, python's scripts directory should already be in your path.  If
commands like ``easy_install`` or ``pip`` already function, you should be good to go.

You should be familiar with IIS and how to load ISAPI extensions into websites
and virtual directories.  You should be familiar with isapi-wsgi setup.

Dependencies
--------------------

* argparse
* isapi_wsgi

Usage
--------------------

The "iwhelper" command is installed when installing the ISAPIWSGIHelper
package.

A virtualenv is recommended, but not required:

    > cd c:\\somewhere\\myproj-venv

    > virtualenv .

    > iwhelper

The above will result in a virtualenv with the addition of a isapi-wsgi
directory in the root of the venv.  Edit ``isapi-wsgi\\appinit.py`` according
to the comments in that file.

Then, setup your website or a virtualdirectory with a wildcard mapping
that uses ``isapi-wsgi\\__loader.dll``.

Features
--------------------

The isapi-wsgi directory created by the ``iwhelper`` command results in
a setup with the following features:

* Easy creation of per-project isapi-wsgi bootstrap directories through the
    ``iwhelper`` command (see above)
* Exceptions are caught and handled appropriately.  No more cryptic 500 status
    responses from IIS.
    * exceptions instantiating the application are initially hidden but can
        be displayed to the browser with a configuration change in _loader.py.
    * exceptions encountered when making a request to the application are
        logged to a file in the isapi-wsgi directory.
* appinit.py provides a simple bridge between isapi-wsgi and your application
* appinit.py provides a mechanism for loading a virtualenv's site-packages dir

Special Troubleshooting w/ _loader.py:
-----------------------------------------

If push comes to shove and you just can't figure out why your application isn't
working, _loader.py provides a special mechanism for running your setup in
a python web server which will give you better exception messages and
automatic reloading of your python files when they are changed.  See the
note at the bottom of _loader.py for details.

A Note About App Pools
------------------------

I use a different app pool for each python website.  When troubleshooting, I set
the app pool to auto-recycle after one request.  This is a close equivalent to
auto-reloading in various python development web servers.  Just remember to
**turn it off** before going to production usage or your performance will suffer
tremendously.

Questions & Comments
---------------------

Please visit: http://groups.google.com/group/blazelibs

Current Status
---------------

Works for me. :)

The `development version <http://bitbucket.org/rsyring/isapi-wsgi-helper/get/tip.zip#egg=IsapiWSGIHelper-dev>`_
is installable with ``easy_install ISAPIWSGIHelper==dev``.
"""
import os
import sys
from setuptools import setup, find_packages

version = "0.1.0"

if sys.platform == 'win32':
    kw = dict(entry_points=dict(console_scripts=['iwhelper=iwhelper.command:main']))
else:
    kw = dict(scripts=['scripts/iwhelper'])

kw.setdefault('entry_points', {})

required_packages = ['isapi_wsgi']
try:
    import argparse
except ImportError:
    required_packages.append('argparse')

setup(name='ISAPIWSGIHelper',
      version=version,
      description="utilities to help bootstrap deployment of WSGI applications using isapi-wsgi",
      long_description=__doc__,
      classifiers=[
        'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
      ],
      author='Randy Syring',
      author_email='rsyring@gmail.com',
      url='http://bitbucket.org/rsyring/isapi-wsgi-helper/',
      license='BSD',
      packages=find_packages(),
      install_requires=required_packages,
      include_package_data=True,
      zip_safe=False,
      **kw)
