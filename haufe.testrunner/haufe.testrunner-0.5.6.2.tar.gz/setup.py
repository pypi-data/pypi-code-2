##########################################################################
# haufe.testrunner  
#
# (C) Haufe Mediengruppe, Freiburg, Germany
##########################################################################

import os
from setuptools import setup, find_packages


CLASSIFIERS = [
    'Programming Language :: Python',
]

version = '0.5.6.2'
desc = open('README.txt').read().strip()
changes = open('CHANGES.txt').read().strip()

long_description = desc + '\n\nChanges:\n========\n\n' + changes


setup(name='haufe.testrunner',
      version=version,
      license='n/a',
      author='Andreas Jung',
      author_email='andreas.jung@haufe.de',
      maintainer='Andreas Jung',
      maintainer_email='andreas.jung@haufe.de',
      classifiers=CLASSIFIERS,
      url='????',
      zip_safe=False,
      description='A wrapper for the Zope testrunner providing email support, HTML generation and RSS support',
      long_description=long_description,
      packages=['haufe', 'haufe.testrunner'],
      include_package_data = True,
      install_requires=['setuptools', 'SQLAlchemy>=0.4.6,<=0.4.99999'],
      namespace_packages=['haufe'],
      entry_points={'console_scripts' : ['htr = haufe.testrunner.cli:main',
                                         'htr_bootstrap = haufe.testrunner.database.bootstrap:main',
                                        ]},
      )

