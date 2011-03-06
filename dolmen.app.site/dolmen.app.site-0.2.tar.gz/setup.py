from setuptools import setup, find_packages
from os.path import join

name = 'dolmen.app.site'
version = '0.2'
readme = open(join('src', 'dolmen', 'app', 'site', 'README.txt')).read()
history = open(join('docs', 'HISTORY.txt')).read()


install_requires = [
    'dolmen.content >= 0.7',
    'grokcore.site',
    'setuptools',
    'zope.interface',
    ]

tests_require = [
    'grokcore.component',
    'zope.app.wsgi',
    'zope.component',
    'zope.event',
    'zope.i18n',
    'zope.lifecycleevent',
    'zope.security',
    'zope.securitypolicy',
    'zope.site',
    ]

setup(name = name,
      version = version,
      description = 'Dolmen CMS',
      long_description = readme + '\n\n' + history,
      keywords = 'Grok Zope3 CMS Dolmen',
      author = 'Souheil Chelfouh',
      author_email = 'trollfot@gmail.com',
      url = 'http://www.dolmen-project.org',
      license = 'ZPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages = ['dolmen', 'dolmen.app'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      tests_require = tests_require,
      install_requires = install_requires,
      extras_require = {'test': tests_require},
      test_suite="dolmen.app.site",
      classifiers = [
          'Environment :: Web Environment',
          'Intended Audience :: Other Audience',
          'License :: OSI Approved :: Zope Public License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          ],
      )
