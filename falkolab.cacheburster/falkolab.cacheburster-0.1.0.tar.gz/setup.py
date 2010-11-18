#############################################################################
#
# Copyright (c) 2010 Falko Lab and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE. 
#
##############################################################################
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
                    read('README.txt')
                    + '\n\n' +
                    read('src', 'falkolab', 'cacheburster', 'README.txt')
                    + '\n\n' +
                    read('CHANGES.txt')
                    )

setup(name='falkolab.cacheburster',
      version='0.1.0',
      description='Manipulations with browser resource URL to forcing a browser to update its cache',
      long_description=long_description,     
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Zope3',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Zope Public License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Internet :: WWW/HTTP',
                   ],
      keywords='resource cache burster hash crc32 version',
      author='Andrey Tkachenko',
      author_email='falko.lab@gmail.com',
      url='http://blog.falkolab.ru',
      license='ZPL 2.1',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages = ['falkolab'],
      include_package_data=True,
      zip_safe=False,
      extras_require={
          'test': ['zope.testing',
                   'zope.app.testing',
                   'zope.testbrowser',
                   'zope.app.zcmlfiles',
                   'zope.security',
                   
                   'zope.app.securitypolicy',
                  ],
          },
      install_requires=['distribute',
                        'zope.component',
                        'zope.interface',
                        'zope.browserresource', 
                        'zope.configuration',  
                        'zope.publisher',
                        'zope.location',
                        'zope.traversing',   
                        'zope.app.appsetup',
                        'zope.app.publisher',
                        ],
    )
