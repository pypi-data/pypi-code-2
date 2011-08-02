
from distutils.core import setup

setup(name='matalg27',
      version='0.1.0',
      description='Pure Python 2.7 Matrix Algebra Module.',
      long_description='''
=====================================
Pure Python 2.7 Linear Algebra Module
=====================================

Introduction
============

This module, written in Python2.7, is the backport of a similar module written in Python 3.2. There are many 
Python users who have not yet moved to Python 3.x and because generally Python 3.x is not fully backwards 
compatible with the earlier Python versions, it has been necessary to provide backports of Python 3.x modules to Python 2.x.

This module, written in pure Python 2.7, does not require other modules, only
Python 2.x. Consequently the module is as portable as Python itself. The well documented module is easy to use and allows use of the usual 
scalar variable syntax for the more complex matrix operations. Thus, for matrix multiplication of matrices **amat** and **bmat** one can simply write::

    resultmat = amat * bmat

For the inversion of **amat**, one only needs to write::

    resultmat = ~ amat

Matrix naming convention is freely chosen by the end user.  The module is well documented with pdf files **quickStart**, **userManual** and **referenceMatalg**. Reference can also be made to the documentation 
of the Python 3.2 module "Matalg". In the backport attention was given to user use compatibility between the 
modules in Python 3.2 and Python 2.7. 

Documentation and Servicing
===========================

**Quick Start** will get an experienced user up to speed very quickly. **User Manual** has an explanation and examples of most capabilities of the package, whilst the **Reference of Matalg** lists all the methods and functions of the module with brief explanation of each. In addition to the supplied pdf files, the information for the Python 2.7 module is also accessible on the web at::

    http://akabaila.pcug.org.au/matalg27-doc/index.html

The author is prepared to consider all reasonable requests for extensions and improvements and/or bug fixes of the module. Your emails will be appreciated::

  algis.kabaila@gmail.com

Licence
========

The module is licensed under LGPL and is Open Source Freeware. You are welcome to copy it and to share it.

Algis Kabaila, Canberra, 2011.
                       ''',
      author='Algis Kabaila',
      author_email='algis.Kabaila@gmail.com',
      url='http://akabaila.pcug.org.au/matalg27-doc/index.html',
      packages=['matalg27'],
      package_dir={'matalg27' : 'matalg27-mod'},    
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
	  'Programming Language :: Python :: 2.7',
	  'Topic :: Education',
	  ],

     )
      
