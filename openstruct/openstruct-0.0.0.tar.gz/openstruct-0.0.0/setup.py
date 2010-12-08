from setuptools import setup

version = '0.0.0'
name = 'openstruct'
short_description = '`openstruct` is a package for lazy person in daily life. porting from ruby'
long_description = """\
`openstruct` is a package for lazy person in daily life. porting from ruby

Requirements
------------
* Python 2.6 or later (not support 3.x)

Features
--------
* OpenStruct
* OpenStructExtend

Setup
-----
::

   $ easy_install openstruct

History
-------
0.0.0 (2010-12-9)
~~~~~~~~~~~~~~~~~~
* first release
"""

classifiers = [
"Development Status :: 1 - Planning", 
"License :: OSI Approved :: Python Software Foundation License", 
"Programming Language :: Python", 
"Topic :: Software Development :: Libraries :: Ruby Modules"
]

setup(name=name,
      version=version,
      description=short_description,
      long_description=long_description,
      classifiers=classifiers,
      keywords=['ruby', 'plactice', 'openstruct'], 
      author = "podhmo", 
      author_email = "ababjam61@gmail.com", 
      license='PSL'
      )
