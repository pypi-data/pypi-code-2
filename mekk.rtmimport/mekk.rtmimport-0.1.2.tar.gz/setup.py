# -*- coding: utf-8 -*-
# (c) 2010, Marcin Kasperski

from setuptools import setup, find_packages

version = '0.1.2'
long_description = open("README.txt").read()
classifiers = [
    "Programming Language :: Python",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries :: Python Modules",
    # TODO: Development Status, Environment, Topic
    ]

setup(name='mekk.rtmimport',
      version=version,
      description="Import foreign (at the moment, Nozbe) data to RememberTheMilk",
      long_description=long_description,
      classifiers=classifiers,
      keywords='rtm,RememberTheMilk',
      author='Marcin Kasperski',
      author_email='Marcin.Kasperski@mekk.waw.pl',
      url='',
      license='LGPL',
      package_dir={'':'src'},
      packages=find_packages('src', exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['mekk'],
      test_suite = 'nose.collector',
      zip_safe=False,
      install_requires=[
        'simplejson', 
        'RtmAPI>=0.3.3', #http://pypi.python.org/pypi/RtmAPI/0.3.1
        'keyring>=0.3',
      ],
      tests_require=[
          'nose', 
      ],
      entry_points = {
        'console_scripts': [
            'rtmimport = mekk.rtmimport.run:run',
            ],
        },

)
