# Copyright (C) 2009-2011  Rene Koecher <shirk@bitspin.org>
#
# This file is part of paraproxy.
#
# Paraproxy is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# Paraproxy is distrubuted in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Paraproxy; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA.


longdesc = '''
This is a supplement library for paramiko which adds support for
SSH2 proxy commands.

Required packages:
    paramiko
'''

# if someday we want to *require* setuptools, uncomment this:
# (it will cause setuptools to be automatically downloaded)
#import ez_setup
#ez_setup.use_setuptools()

import sys
try:
    from setuptools import setup
    kw = {
        'install_requires': 'paramiko >= 1.7.4',
    }
except ImportError:
    from distutils.core import setup
    kw = {}
    
if sys.platform == 'darwin':
	import setup_helper
	setup_helper.install_custom_make_tarball()


setup(name = "paraproxy",
      version = "1.2",
      description = "Paramiko addon for SSH2 ProxyCommands",
      author = "Rene Koecher",
      author_email = "shirk AT bitspin DOT org",
      url = "http://pypi.python.org/pypi/paraproxy/",
      packages = [ 'paraproxy' ],
      license = 'LGPL',
      platforms = 'Posix; MacOS X',
      classifiers = [ 'Development Status :: 4 - Beta',
                      'Intended Audience :: Developers',
                      'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
                      'Operating System :: OS Independent',
                      'Topic :: Internet',
                      'Topic :: Security :: Cryptography' ],
      long_description = longdesc,
      **kw
      )
