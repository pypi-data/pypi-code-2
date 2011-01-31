# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from os.path import join

name = 'dolmen.menu'
version = '0.5'
readme = open(join('src', 'dolmen', 'menu', "README.txt")).read()
history = open(join('docs', 'HISTORY.txt')).read()

install_requires = [
    'setuptools',
    'grokcore.component',
    'grokcore.viewlet',
    'grokcore.view',
    'megrok.pagetemplate',
    'martian',
    'zope.location',
    'zope.interface',
    'zope.security',
    'zope.component',
    'zope.publisher',
    'zope.schema',
    'zope.security',
    'zope.traversing',
    'zope.viewlet',
    ]

tests_require = [
    'zope.securitypolicy',
    'zope.location',
    'grokcore.security',
    'zope.site',
    'zope.container',
    'zope.i18n',
    'zope.principalregistry',
    ]

setup(name = name,
      version = version,
      description = 'Dolmen menus composer',
      long_description = readme + '\n\n' + history,
      keywords = 'Grok Zope3 CMS Dolmen',
      author = 'Souheil Chelfouh',
      author_email = 'trollfot@gmail.com',
      url = '',
      license = 'GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages = ['dolmen'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      tests_require = tests_require,
      install_requires = install_requires,
      extras_require = {'test': tests_require},
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Zope3',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ],
      )
