#!/usr/bin/env python
from distutils.core import setup

readme = open('README.txt').read()
conf = dict(
    name='alart',
    version='0.1.1',
    author='Niels Serup',
    author_email='ns@metanohi.name',
    package_dir={'': '.'},
    py_modules = ['alart'],
    scripts=['alart'],
    url='http://metanohi.name/projects/alart/',
    license='GPLv3+',
    description='Generate pseudo-random art',
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: End Users/Desktop',
                 'Intended Audience :: Developers',
                 'Topic :: Multimedia :: Graphics',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 'Topic :: Utilities',
                 'Environment :: Console',
                 'Environment :: X11 Applications',
                 'License :: DFSG approved',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python'
                 ],
    requires=['cairo']
)

try:
    # setup.py register wants unicode data..
    conf['long_description'] = readme.decode('utf-8')
    setup(**conf)
except Exception:
    # ..but setup.py sdist upload wants byte data
    conf['long_description'] = readme
    setup(**conf)
