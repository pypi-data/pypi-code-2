"""
Web2py Utils
============

Contains lots of goodies for use with web2py and web development

About
=====

After using web2py for quite a while I have an eclectic mix of utilities that 
I seem to be using for almost every web2py app I develop now!

I needed both a way to organize the same code across multiple web2py apps and I
also wanted to share this code with the world!

Lots of Goodies!
================

* Common shortcuts
* py2jquery module
* Heirarchical category module.
* Database store configuration settings
* Class based menu builder
* syntax highlighting
* Output compression
* Pagination
* Stop words lists
* Levenstien algorithm
* NGram algorithm
* New SQLHTML widgets (able to pass class attributes to them)
* Convert wordpress xml export into a python dict!
* Comments, tagging, and pingback/trackback plugins!
* Unittesting, code coverage.
"""

from setuptools import setup, find_packages
import sys, os

from web2py_utils import __VERSION__, __RELEASE__

version = __VERSION__

setup(name='web2py_utils',
      version=version,
      description="Web2py Utilities",
      long_description=__doc__,
      keywords='web2py',
      author='Thadeus Burgess',
      author_email='thadeusb@thadeusb.com',
      url='http://packages.python.org/web2py_utils/',
      license='GPL v3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
      ],
      entry_points="""
      """,
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
      ],
      )
