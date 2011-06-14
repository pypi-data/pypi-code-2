# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from os.path import join

name = 'dolmen.content'
version = '2.0a2'
readme = open(join('src', 'dolmen', 'content', 'README.txt')).read()
history = open(join('docs', 'HISTORY.txt')).read()

install_requires = [
    'ZODB3 >= 3.10',  # Persistent.
    'cromlech.container',
    'dolmen.container >= 0.2',
    'dolmen.field >= 0.3',
    'grokcore.component >= 2.4',
    'grokcore.security',
    'martian >= 0.14',
    'setuptools',
    'zope.component',
    'zope.i18nmessageid',
    'zope.interface',
    'zope.schema',
    ]

tests_require = [
    'zope.location',
    'zope.testing',
    ]

setup(name=name,
      version=version,
      description='Dolmen content type framework',
      long_description=readme + '\n\n' + history,
      keywords='Grok Dolmen Content',
      author='The Dolmen team',
      author_email='dolmen@list.dolmen-project.org',
      url='http://gitweb.dolmen-project.org/',
      download_url='',
      license='ZPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['dolmen'],
      include_package_data=True,
      platforms='Any',
      zip_safe=False,
      tests_require=tests_require,
      install_requires=install_requires,
      extras_require={'test': tests_require},
      classifiers=[
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
      ],
)
