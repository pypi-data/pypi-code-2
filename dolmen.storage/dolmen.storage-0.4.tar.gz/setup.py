from os.path import join
from setuptools import setup, find_packages

name = 'dolmen.storage'
version = '0.4'
readme = open(join('src', 'dolmen', 'storage', 'README.txt')).read()
history = open(join('docs', 'HISTORY.txt')).read()

install_requires = [
    'ZODB3',
    'grokcore.component',
    'setuptools',
    'zope.annotation',
    'zope.component >= 3.9.1',
    'zope.container',
    'zope.interface',
    'zope.location',
    'zope.schema',
    ]

tests_require = [
    'zope.container',
    'zope.testing',
    'zope.traversing',
    'zope.site',
    ]

setup(name = name,
      version = version,
      description = 'Dolmen Zope3 Grok Storage Annotation',
      long_description = readme + '\n\n' + history,
      keywords = 'Grok Zope3 CMS Dolmen',
      author = 'Souheil Chelfouh',
      author_email = 'trollfot@gmail.com',
      url = 'http://gitweb.dolmen-project.org',
      download_url = '',
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
