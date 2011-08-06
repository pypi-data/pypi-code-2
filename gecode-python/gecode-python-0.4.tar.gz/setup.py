## -*- python -*-
##=============================================================================
## Copyright (C) 2011 by Denys Duchier
##
## This program is free software: you can redistribute it and/or modify it
## under the terms of the GNU Lesser General Public License as published by the
## Free Software Foundation, either version 3 of the License, or (at your
## option) any later version.
## 
## This program is distributed in the hope that it will be useful, but WITHOUT
## ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
## FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
## more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with this program.  If not, see <http:##www.gnu.org/licenses/>.
##=============================================================================

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

from code_generator import generate_files

class gecode_build_ext(build_ext):

    def run(self):
        generate_files()
        build_ext.run(self)

from distutils.command.clean import clean

class gecode_clean(clean):

    def run(self):
        import glob
        import os
        todo = []
        todo.extend(glob.glob("*.pxi"))
        todo.extend(glob.glob("*~"))
        todo.extend(glob.glob("*.pyc"))
        todo.append("_gecode.cpp")
        for x in todo:
            try:
                os.unlink(x)
            except:
                pass
        clean.run(self)

setup(
    name='gecode-python',
    description="bindings for the Gecode constraint-programming library",
    author="Denys Duchier",
    author_email="denys.duchier@univ-orleans.fr",
    version="0.4",
    url="https://launchpad.net/gecode-python",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Programming Language :: Python",
        "Programming Language :: Cython",
        "Programming Language :: C++",
        "Topic :: Software Development :: Libraries :: Python Modules"
        ],
    requires=["Cython(>=0.14.1)"],
    package_dir={ "gecode" : "" },
    py_modules=["gecode.__init__", "gecode.boundvar"],
    ext_modules=[ 
        Extension("gecode._gecode",
                  sources=["_gecode.pyx"],
                  define_macros=[("DISJUNCTOR",None)],
                  libraries=["stdc++", "gecodeint", "gecodeset", "gecodesearch", "gecodekernel", "gecodesupport"],
                  language="c++"
                  ),
        ],
    cmdclass = {'build_ext': gecode_build_ext,
                'clean' : gecode_clean },
    )
