
from distutils.core import setup

setup(name='Matalg',
      version='0.1.0',
      description='Pure Python3 Matrix Algebra Module.',
      long_description='''
==================================
Pure Python3 Linear Algebra Module
==================================

Introduction
============

This module, written in pure Python 3.2, does not require other modules, only
Python 3.2 or higher. Consequently the module is as portable as Python3 itself. The well documented module is easy to use and allows use of the usual
scalar variable syntax for the more complex matrix operations. Thus, for matrix multiplication of matrices **amat** and **bmat** one writes simply::

    resultmat = amat * bmat

For the inversion of **amat**, one only needs to write::

    resultmat = ~ amat

Matrix naming convention is freely chosen by the end user.  The module is well documented with pdf files **quickStart**, **userManual** and **referenceMatalg**. 

Documentation and Servicing
===========================

**Quick Start** will get an experienced user up to speed very quickly. **User Manual** has an explanation and examples of most capabilities of the package, whilst the **Reference of Matalg** lists all the methods and functions of the module with brief explanation of each. In addition to the supplied pdf files, the information is also accessible on the web at::

    http://akabaila.pcug.org.au/matalg-doc/index.html

The author is an experienced university lecturer and professor, who is prepared in his retirement to consider all reasonable requests for extensions and improvements and/or bug fixes of the module. Your emails will be appreciated::

  algis.kabaila@gmail.com

Last but not least, this module is ideal for the period of transition between Python2.x and Python3.x, as it is powerful enough for medium size examples of several hundred simultaneous linear equations whilst considerably more extensive numerical analysis packages are not readily available in most popular Linux distributions. The development and initial testing of the package was on a kubuntu 11.04 "natty" platform.

Licence
========

The module is licensed under LGPL and is Open Source Freeware. You are welcome to copy it and to share it.

Algis Kabaila, Canberra, 2011.
                       ''',
      author='Algis Kabaila',
      author_email='algis.Kabaila@gmail.com',
      url='http://akabaila.pcug.org.au/matalg-doc/index.html',
      packages=['matalg'],
      package_dir={'matalg' : 'matalg-mod'},
      package_data={'matalg' : ['matalg-pdf/*.pdf', 'matalg-rst/*.rst']},      
      platforms='POSIX',
      license='LGPL',      
      classifiers=[
          'Development Status :: 5 - Production/Stable',
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
      
