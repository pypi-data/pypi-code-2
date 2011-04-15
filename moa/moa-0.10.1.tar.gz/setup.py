#!/usr/bin/env python

import os
#from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES
from setuptools import setup
# see:
# http://groups.google.com/group/comp.lang.python/browse_thread/\
#      thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

with open('VERSION') as F:
    version = F.read().strip()

scripts  = [os.path.join('bin', x) for x in """
moa        fastaSplitter  fastaNfinder  fastaInfo  fastaExtract
fasta2gff  blastReport    blastInfo     blast2gff  moaprompt
moainit
""".split()]

data_files = []
template_data = []
exclude = ['build', 'sphinx', 'debian', 'dist', 'util']
for dirpath, dirnames, filenames in os.walk('.'):
    for dirname in enumerate(dirnames):
        if dirname[0] == '.': dirnames.remove(dirname)
        if dirpath == '.' and  dirname in exclude: dirnames.remove(dirname)
    for filename in filenames:
        if filename[-1] == '~': filenames.remove(filename)
    if '__init__.py' in filenames: continue
    #np = os.path.join('./', dirpath)
    if dirpath[0] == '/':
        np = dirpath[1:]
    elif dirpath[:2] == './':
        np = dirpath[2:]
    else: np = dirpath
    data_files.append([np, [os.path.join(dirpath, f) for f in filenames]])

#import pprint
#pprint.pprint(data_files)
#data_files.append(['/etc/bash_completion.d/', ['etc/bash_completion.d/moa']])
data_files.append(('/etc/moa', ['etc/config']))
data_files.append(('/etc/bash_completion.d/', ['etc/bash_completion.d/moa']))
setup(name='moa',
      version=version,
      description='Moa - lightweight bioinformatics pipelines',
      author='Mark Fiers',
      author_email='mark.fiers@plantandfood.co.nz',
      url='http://mfiers.github.com/Moa/',
      packages=['moa', 'moa.plugin', 'moa.backend', 'Yaco', 'fist'],
      package_dir = {'': os.path.join('lib', 'python')},
      scripts = scripts,
      data_files = data_files,
      requires = [
          'Jinja2 (>2.0)',
          'biopython (>1.50)',
          'GitPython (>0.3)',
          ],
      classifiers = [
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Unix Shell',
          'Topic :: Scientific/Engineering :: Bio-Informatics'
          ]
     )
