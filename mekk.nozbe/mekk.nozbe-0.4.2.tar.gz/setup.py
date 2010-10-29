# -*- coding: utf-8 -*-
# (c) 2008-2009, Marcin Kasperski

from setuptools import setup, find_packages

version = '0.4.2'
long_description = open("README.txt").read()

classifiers = [
    "Programming Language :: Python",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries :: Python Modules",
    # TODO: Development Status, Environment, Topic
    ]

setup(name='mekk.nozbe',
      version=version,
      description="Nozbe interface wrapper.",
      long_description=long_description,
      classifiers=classifiers,
      keywords='nozbe',
      author='Marcin Kasperski',
      author_email='Marcin.Kasperski@mekk.waw.pl',
      url='http://bitbucket.org/Mekk/mekk.nozbe/',
      license='Artistic',
      package_dir={'':'src'},
      packages=find_packages('src', exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['mekk'],
      test_suite = 'nose.collector',
      include_package_data = True,
      zip_safe=False,
      install_requires=[
          'Twisted', 'simplejson', 'keyring',
      ],
      entry_points = {
        'console_scripts' : [
            'nozbetool = mekk.nozbe.run:run',
            ],
        },
)
