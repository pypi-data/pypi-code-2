# -*- coding: utf-8 -*-

from os.path import join
from setuptools import setup, find_packages

version = '0.4'
name = 'menhir.contenttype.image'

history = open(join('docs', 'HISTORY.txt')).read()
readme = open(
    join('src', 'menhir', 'contenttype', 'image', 'README.txt')).read()

tests_require = [
    'zope.i18n',
    'zope.component',
    'zope.container',
    'zope.principalregistry',
    'zope.publisher',
    'zope.security',
    'zope.securitypolicy',
    'zope.site',
    'zope.traversing',
    ]

setup(name = name,
      version = version,
      description = 'Dolmen content-type extension : image',
      long_description = readme[readme.find('\n\n'):] + '\n' + history,
      keywords = 'Grok Zope3 CMS Dolmen',
      author = 'Souheil Chelfouh',
      author_email = 'souheil@chelfouh.com',
      url = 'http://tracker.trollfot.org/',
      download_url = 'http://pypi.python.org/pypi/menhir.contenttype.image',
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
          'dolmen.app.content >= 1.0b1',
          'dolmen.app.layout',
          'dolmen.app.security',
          'dolmen.blob',
          'dolmen.content >= 0.7',
          'dolmen.file',
          'dolmen.thumbnailer',
          'dolmen.widget.image',
          'fanstatic',
          'grokcore.view',
          'js.jquery_slimbox',
          'setuptools',
          'zope.i18nmessageid',
          'zope.size',
      ],
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Zope3',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [fanstatic.libraries]
      popup = menhir.contenttype.image.library:ImageLibrary
      """,
)
