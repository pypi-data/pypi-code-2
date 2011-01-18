#!/usr/bin/env python

import os
import sys
from distutils.core import setup

import authenticity

macros = [('MODULE_VERSION', '%s' % authenticity.__version__)]

def subtree(target, directory):
    return [('%s/%s' % (target, parent), ['%s/%s' % (parent, file) for file in files]) for parent, _, files in os.walk(directory) if files]

setup(name          = 'authenticity',
      version       = authenticity.__version__,
      description   = 'OpenID Server running on mod_python and using a LDAP directory',
      url           = authenticity.__homepage__,
      author        = 'Luci Stanescu',
      author_email  = 'luci@cnix.ro',
      license       = 'GPL-2',
      platforms     = ['POSIX'],
      classifiers   = [
            #'Development Status :: 1 - Planning',
            #'Development Status :: 2 - Pre-Alpha',
            'Development Status :: 3 - Alpha',
            #'Development Status :: 4 - Beta',
            #'Development Status :: 5 - Production/Stable',
            #'Development Status :: 6 - Mature',
            #'Development Status :: 7 - Inactive,
            'Framework :: Twisted',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: POSIX',
            'Programming Language :: Python',
            'Topic :: Internet',
            'Topic :: Security'],
      packages      = ['authenticity'],
      scripts       = [],
      data_files    = subtree('share/authenticity', 'templates')+
                      subtree('share/authenticity', 'xrds'),
      requires      = ['genshi', 'ldap', 'openid', 'zope.interface'],
      provides      = ['authenticity']
)

