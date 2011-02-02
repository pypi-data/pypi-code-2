from setuptools import setup, find_packages
from os.path import join

name = 'dolmen.app.container'
version = '1.0b1'
readme = open(join("src", "dolmen", "app", "container", "README.txt")).read()
history = open(join('docs', 'HISTORY.txt')).read()

install_requires=[
    'ZODB3',
    'dolmen.app.layout >= 1.0b1',
    'dolmen.app.security',
    'dolmen.content >= 0.6.1',
    'dolmen.menu',
    'grokcore.component',
    'grokcore.view',
    'grokcore.viewlet',
    'megrok.z3ctable >= 1.5.0',
    'setuptools',
    'zope.component',
    'zope.container',
    'zope.dublincore',
    'zope.i18n',
    'zope.i18nmessageid',
    'zope.interface',
    'zope.security',
    ]

tests_require = [
    'zope.configuration',
    'zope.principalregistry',
    'zope.publisher',
    'zope.securitypolicy',
    'zope.site',
    'zope.testing',
    'zope.traversing',
    ]

setup(name = name,
      version = version,
      description = 'Containers tools for Dolmen applications',
      long_description = readme + '\n\n' + history,
      keywords = 'Grok Zope3 CMS Dolmen',
      author = 'Souheil Chelfouh',
      author_email = 'trollfot@gmail.com',
      url = 'http://gitweb.dolmen-project.org/',
      download_url = '',
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
      test_suite="dolmen.app.container",
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
