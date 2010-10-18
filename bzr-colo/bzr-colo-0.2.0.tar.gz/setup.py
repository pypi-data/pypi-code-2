#!/usr/bin/env python
from distutils.core import setup

from info import (bzr_plugin_version,
                  bzr_plugin_name,
                  bzr_minimum_version,
                  bzr_commands,
                  __version__,
                 )

if __name__ == '__main__':
    setup(name="bzr-colo",
          version=__version__,
          description="Work with colocated Bazaar branches "
                      "using current technology.",
          author="Neil Martinsen-Burrell",
          author_email="nmb@wartburg.edu",
          url="https://launchpad.net/bzr-colo`",
          packages=['bzrlib.plugins.colo',
                    'bzrlib.plugins.colo.tests',
                    'bzrlib.plugins.colo.explorer',
                    ],
          package_dir={'bzrlib.plugins.colo': '.'},
          classifiers=['Development Status :: 4 - Beta',
                       'Intended Audience :: Developers',
                       'License :: OSI Approved :: GNU General Public License (GPL)',
                       'Programming Language :: Python :: 2',
                       'Topic :: Software Development :: Version Control',
                      ]
          
         )
