#!/usr/bin/env python

from distutils.core import setup, Command
from distutils.command.build import build
from distutils.command.clean import clean
import os
import sys
import subprocess


class build_custom(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # build the manpage
        subprocess.check_call(['pandoc', '-s', '-w', 'man', 'purity-ng.1.md', '-o', 'purity-ng.1'])
        # create the symlink so setup works properly

class clean_all(Command):
    user_options = []
    
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        delme = ['purity-ng.1']
        for path in delme:
            try:
                os.remove(path)
            except OSError as e:
                if e.errno != 2:
                    # 2 is file not found
                    raise e


build.sub_commands.append(('build_custom', None))
clean.sub_commands.append(('clean_all', None))

setup(name='purity-ng',
      version='0.1',
      description='general purpose purity testing software',
      author='Simon Fondrie-Teitler',
      author_email='simonf@riseup.net',
      url='http://launchpad.net/purity-ng',
      scripts=['purity-ng'],
      data_files=[('/usr/share/man/man6/', ['purity-ng.1'])],
      cmdclass={'build_custom': build_custom, 'clean_all': clean_all}
     )
