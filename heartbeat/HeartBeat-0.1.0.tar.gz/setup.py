#!/usr/bin/env python
from distutils.core import setup

setup(name='HeartBeat',
      version='0.1.0',
      description='Yet Another HeartBeat',
      author='Sameer Rahmani',
      author_email='lxsameer@gnu.org',
      url='http://git.lxsameer.com/?p=heartbeat.git;a=summary',
      license='GPL v2',
      scripts=["heartbeat", "heartbeatd"],
      data_files=[("/usr/share/man/man1/", ["man/heartbeatd.1"]),
                  ("/usr/share/man/man1/", ["man/heartbeat.1"]),
                  ("/etc/heartbeat/", ["conf/heartbeat.conf"]),
                  ("/etc/heartbeat/", ["conf/hosts.db"]),
                  ("/etc/init.d/", ["init/heartbeatd"]),
                  ],
      packages=['hbeat', 'hbeat.logging'],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities',
          ]
)
