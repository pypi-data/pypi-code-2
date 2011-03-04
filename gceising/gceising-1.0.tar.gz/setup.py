#!/usr/bin/env python

from distutils.core import setup, Extension
from distutils.file_util import copy_file
import os

from numpy.distutils.misc_util import get_numpy_include_dirs
npy_incdir = get_numpy_include_dirs()


PAKNAME = 'gceising'

if os.path.exists('MANIFEST'):
    os.remove('MANIFEST')#created from 'MANIFEST.in'

#cd ext-swig   
#swig -c++ -python -Iext-swig -modern -o Ising_wrap.cpp Ising.i
if os.path.exists(os.path.join('ext-swig', 'Ising.py')):
    copy_file(os.path.join('ext-swig', 'Ising.py'),os.path.join(PAKNAME, 'Ising.py'))

SOURCE = [os.path.join('ext-swig', fi) for fi  in['Ising_wrap.cpp', 'Ising.cpp', 'Random.cpp']]
Ising_swig = Extension(PAKNAME+'._Ising', SOURCE, include_dirs=["ext-swig"] + npy_incdir, library_dirs=[], libraries=[])
setup(name=PAKNAME,
      version='1.0',
      description="Monte Carlo simulator of Generalized Canonical Ensemble of Ising Model",
      long_description=open("README.txt").read(),
      #install_requires=['numpy','matplotlib','Pyqt4'],
      author='Alwin Tsui',
      author_email='alwintsui@gmail.com',
      url='http://code.google.com/p/gce-ising/',
      download_url="http://code.google.com/p/gce-ising/downloads/list",
      platforms=['any'],
      license="GPLv3+",
      packages=[PAKNAME],
      ext_modules=[Ising_swig],
      classifiers=[
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python'],
     )