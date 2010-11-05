from setuptools import setup, find_packages
from os.path import join

name = 'dolmen.app.search'
version = '0.4'
readme = open(join('src', 'dolmen', 'app', 'search', 'README.txt')).read()
history = open(join('docs', 'HISTORY.txt')).read()

install_requires = [
    'dolmen.app.layout',
    'dolmen.app.security',
    'grokcore.security',
    'grokcore.viewlet',
    'martian',
    'setuptools',
    'zope.catalog',
    'zope.component',
    'zope.i18n',
    'zope.i18nmessageid',
    'zope.interface',
    'zope.intid',
    'zope.schema',
    'zope.security',
    ]

tests_require = [
    'grok',
    'zope.app.wsgi',
    'zope.index',
    'zope.publisher',
    'zope.site',
    ]

setup(name = name,
      version = version,
      description = 'Catalog search utilities for Grok applications',
      long_description = readme + '\n\n' + history,
      keywords = 'Grok Zope3 CMS Dolmen',
      author = 'Souheil Chelfouh',
      author_email = 'trollfot@gmail.com',
      url = 'http://gitweb.dolmen-project.org',
      license = 'GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages = ['dolmen', 'dolmen.app'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      tests_require = tests_require,
      install_requires = install_requires,
      extras_require = {'test': tests_require},
      classifiers = [
        'Environment :: Web Environment',
        'Framework :: Zope3',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
      ],
)
