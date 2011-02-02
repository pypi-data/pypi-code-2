# -*- coding: utf-8 -*-

from os.path import join
from setuptools import setup, find_packages

version = '0.3'
name = 'menhir.contenttype.photoalbum'

history = open(join('docs', 'HISTORY.txt')).read()
readme = open(
    join('src', 'menhir', 'contenttype', 'photoalbum', 'README.txt')).read()

tests_require = [
    "ZODB3",
    "zope.annotation",
    "zope.app.appsetup",
    "zope.app.publication",
    "zope.browserpage",
    "zope.dublincore",
    "zope.fanstatic",
    "zope.keyreference",
    "zope.principalregistry",
    "zope.publisher",
    "zope.security",
    "zope.securitypolicy",
    "zope.site",
    "zope.traversing",
    ]

setup(name = name,
      version = version,
      description = 'Dolmen contenttype extension : photoalbum',
      long_description = readme + '\n\n' + history,
      keywords = 'Grok Zope3 CMS Dolmen',
      author = 'Souheil Chelfouh',
      author_email = 'trollfot@gmail.com',
      url = 'http://www.dolmen-project.org',
      download_url = '',
      license = 'GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages = ['menhir', 'menhir.contenttype'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      install_requires=[
          'dolmen.app.content',
          'dolmen.app.layout',
          'dolmen.app.security',
          'dolmen.app.viewselector',
          'dolmen.content',
          'dolmen.menu',
          'fanstatic',
          'grokcore.component',
          'js.galleriffic >= 2.0.1-1',
          'megrok.chameleon',
          'menhir.contenttype.image >= 0.3',
          'setuptools',
          'zope.component',
          'zope.container',
          'zope.i18n',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.intid',
          ],
      classifiers = [
          'Environment :: Web Environment',
          'Intended Audience :: Other Audience',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          ],
      entry_points="""
      # -*- Entry points: -*-
      [fanstatic.libraries]
      galleries = menhir.contenttype.photoalbum.libraries:GalleryResources
      """,
      )
