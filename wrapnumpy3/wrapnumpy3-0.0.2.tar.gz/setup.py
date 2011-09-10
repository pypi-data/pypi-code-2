
from distutils.core import setup

setup(name='wrapnumpy3',
      version='0.0.2',
      description='Wrapper of Numpy in Python3.',
      long_description='''
===============================================
Wrapper of Numpy in Python3 for Matrix Algebra.
===============================================

Introduction
============

This Python 3.2 wrapper module, requires Numpy to be installed. For a slower module that is written in pure Python, consider "Matalg".

The well documented module is easy to use and allows use of the usual
scalar variable syntax for the more complex matrix operations. Thus, for matrix multiplication of matrices  **ma** and **mb** one simply writes::

    result = ma * mb

It is assumed that all elements of matrices are floats.
For the solution of equations ma * x = rhs (with unknown x = result), one only needs to write::

    result = ma ** rhs

Matrix naming is left to the end user.  The module is well documented with pdf files **quickStart**, **userManual** and **referenceManual**. 

Documentation and Servicing
===========================

**Quick Start** will get an experienced user up to speed very quickly. **User Manual** has an explanation and examples of most capabilities of the package, whilst the **Reference Manual** lists all the methods and functions of the module with a brief explanation of each. In addition to the supplied pdf files, the information may also be accessible on the web at::

    http://akabaila.pcug.org.au/wrapnumpy3/index.html

The author is interested in your comments of this project and will consider all reasonable requests for extensions and improvements and/or bug fixes of the module. Your emails will be appreciated::

  algis.kabaila@gmail.com

The development and initial testing of the package was on a kubuntu 11.04 "natty" platform.

Licence
========

The module is licensed under GPL and is Open Source Freeware. You are welcome to copy it and to share it.

Algis Kabaila, Canberra, 2011.

                       ''',
      author='Algis Kabaila',
      author_email='algis.Kabaila@gmail.com',
      url='http://akabaila.pcug.org.au/StructuralAnalysis.pdf',
      packages=['wrapnumpy3'],
      package_dir={'wrapnumpy3' : 'wrapnp3-mod'},
      platforms='POSIX',
      license='GPL',      
      classifiers=[
          'Development Status :: 4 - Beta',
	  'Environment :: Console',
	  'Intended Audience :: End Users/Desktop',
	  'Intended Audience :: Developers',
	  'License :: OSI Approved :: GNU General Public License (GPL)',
	  'Operating System :: POSIX',
	  'Programming Language :: Python',
	  'Programming Language :: Python :: 3.2',
	  'Topic :: Education',
	  ],

     )
      
