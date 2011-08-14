
from distutils.core import setup

setup(name='vectors32',
      version='0.0.5',
      description='Pure Python3 Vector Algebra Module.',
      long_description='''
==============================
Python3 Vector Algebra Module
==============================

Introduction
============

This module, written in pure Python 3.2, does not require other modules, only
Python 3.2 or higher. Consequently the module is as portable as Python3 itself. The well documented module is easy to use and allows use of the usual
scalar variable syntax for the more complex vector operations. Thus, for vector scalar multiplication (aka dot product) of vectors **va** and **vb** one simply writes::

    scalarresult = va * vb

For the vector product of vectors **va** and **vb**, one only needs to write::

    vectorresult = va ** vb

Vector naming is left to the end user.  The module is well documented with pdf files **quickStart**, **userManual** and **referenceVectors32**. 

Documentation and Servicing
===========================

**Quick Start** will get an experienced user up to speed very quickly. **User Manual** has an explanation and examples of most capabilities of the package, whilst the **Reference of Vectors32** lists all the methods and functions of the module with a brief explanation of each. In addition to the supplied pdf files, the information may also be accessible on the web at::

    http://akabaila.pcug.org.au/vectors32/index.html

The author plans to spend his retirement years to program open source software. He will be interested in your comments of this project and will consider all reasonable requests for extensions and improvements and/or bug fixes of the module. Your emails will be appreciated::

  algis.kabaila@gmail.com

The development and initial testing of the package was on a kubuntu 11.04 "natty" platform.

Licence
========

The module is licensed under LGPL and is Open Source Freeware. You are welcome to copy it and to share it.

Algis Kabaila, Canberra, 2011.
                       ''',
      author='Algis Kabaila',
      author_email='algis.Kabaila@gmail.com',
      url='http://akabaila.pcug.org.au/StructuralAnalysis.pdf',
      packages=['vectors32'],
      package_dir={'vectors32' : 'vectors32-mod'},
      platforms='POSIX',
      license='LGPL',      
      classifiers=[
          'Development Status :: 4 - Beta',
	  'Environment :: Console',
	  'Intended Audience :: End Users/Desktop',
	  'Intended Audience :: Developers',
	  'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
	  'Operating System :: POSIX',
	  'Programming Language :: Python',
	  'Programming Language :: Python :: 3.2',
	  'Topic :: Education',
	  ],

     )
      
