#!/usr/bin/env python
#
# Copyright (c) 2008-2010 Thomas Lotze
# See also LICENSE.txt

"""A zc.buildout recipe for installing pygtk, pyobject and pycairo.

"""

import os.path
import glob
from setuptools import setup, find_packages


project_path = lambda *names: os.path.join(os.path.dirname(__file__), *names)

longdesc = "\n\n".join((open(project_path("README.txt")).read(),
                        open(project_path("ABOUT.txt")).read()))

data_files = [("", glob.glob(project_path("*.txt")))]

setup_requires = [
    "setuptools_hg",
    ]

install_requires = [
    "setuptools",
    "zc.recipe.cmmi",
    ]

classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: X11 Applications :: GTK",
    "Environment :: Plugins",
    "Framework :: Buildout",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Zope Public License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Topic :: Software Development :: Build Tools",
    "Topic :: System :: Software Distribution",
    ]

entry_points = """\
    [zc.buildout]
    default = tl.buildout_gtk.recipe:InstallPyGTK
    """

setup(name="tl.buildout_gtk",
      version='0.2.2',
      description=__doc__.strip(),
      long_description=longdesc,
      keywords="gtk gobject cairo pygtk pygobject pycairo buildout recipe",
      classifiers=classifiers,
      author="Thomas Lotze",
      author_email="thomas@thomas-lotze.de",
      url="http://www.thomas-lotze.de/en/software/buildout-recipes/",
      license="ZPL 2.1",
      packages=find_packages(),
      setup_requires=setup_requires,
      install_requires=install_requires,
      include_package_data=True,
      data_files=data_files,
      entry_points=entry_points,
      namespace_packages=["tl"],
      zip_safe=False,
      )
