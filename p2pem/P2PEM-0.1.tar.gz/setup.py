#!/usr/bin/env python

from distutils.core import setup

setup(name='P2PEM',
      version='0.1',
      description="General emulation framework for testing of peer-to-peer applications aiming to be highly usable, configurable and extensible.",
      author='Slavka Jaromerska',
      author_email='slavkajaromerska@gmail.com',
      packages=['P2PEM', 'P2PEM.manager', 'P2PEM.director', 'P2PEM.scripts'],
      scripts=['P2PEM/scripts/launch_director.py', 'P2PEM/scripts/launch_manager.py'],
      package_data={'P2PEM.manager': ['fixsrcip-0.1/*', 'force_bind-0.4/*'],},
      requires=['shapytc'],
      license="GNU General Public License (GPL)",
      
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Natural Language :: English',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: System :: Emulators',
          'Topic :: System :: Networking',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
     )