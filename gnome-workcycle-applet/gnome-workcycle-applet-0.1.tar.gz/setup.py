#!/usr/bin/env python
from distutils.core import setup
from distutils.command.install_data import install_data
import subprocess
import os

class post_install(install_data):
    def run(self):
        install_data.run(self)
        subprocess.call(["gconftool-2", "--install-schema-file", os.path.abspath('') + "/schemas/gnome-workcycle-applet.schemas"])
        

setup(name          = 'gnome-workcycle-applet',
      version       = '0.1',
      description   = 'A simple time-management utiliy.',
      author        = 'daddz',
      url           = 'http://github.com/daddz/gnome-workcycle-applet/',
      packages      = ['workcycle'],
      scripts       = ['gnome-workcycle-applet'],
      data_files    = [('/usr/lib/bonobo/servers', ['GNOME_WorkcycleApplet.server'])],
      cmdclass      = dict(install_data = post_install),
      classifiers=[
      'Development Status :: 3 - Alpha',
      'Environment :: X11 Applications :: Gnome',
      'Intended Audience :: End Users/Desktop',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License (GPL)',
      'Operating System :: POSIX :: Linux',
      'Programming Language :: Python',
      'Topic :: Desktop Environment :: Gnome',
      'Topic :: Software Development'
      ]
)
