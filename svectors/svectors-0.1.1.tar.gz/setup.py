# -*- encoding: utf-8

import sys
version = sys.version_info[:2]
if version < (3, 0):
    print("svectors requires Python 3.0 or later! " +
          "(currently running Python %d.%d)" % version)
    sys.exit(1)


from distutils.core import setup, Extension

ext = Extension("_svectors", sources=["src/_svectors.c"])

setup(name="svectors",
      version="0.1.1",
      description="Efficient implementation of dot product and bounded Jiang-Conrath similarity",
      author="Hagen Fürstenau",
      author_email="hagenf"+"\x40"+"coli.uni-saarland.de",
      license="GPL",
      url="http://www.coli.uni-saarland.de/~hagenf/software/svectors/",
      classifiers=[
          "Development Status :: 4 - Beta",
          "Operating System :: OS Independent",
          "Intended Audience :: Science/Research",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.0",
          "Programming Language :: Python :: 3.1"
      ],
      package_dir={"":"src"},
      py_modules=["svectors"],
      ext_modules=[ext]
)
