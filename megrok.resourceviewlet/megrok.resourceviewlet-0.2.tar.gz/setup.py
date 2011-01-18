# -*- coding: utf-8 -*-

from os.path import join
from setuptools import setup, find_packages

version = '0.2'
name = 'megrok.resourceviewlet'

history = open(join('docs', 'HISTORY.txt')).read()
readme = open(join('src', 'megrok', 'resourceviewlet', 'README.txt')).read()

test_requires = [
    'grokcore.component',
    'grokcore.view',
    'zope.annotation',
    'zope.app.appsetup',
    'zope.app.publication',
    'zope.app.wsgi',
    'zope.browserpage',
    'zope.component',
    'zope.container',
    'zope.fanstatic [test]',
    'zope.interface',
    'zope.principalregistry',
    'zope.publisher',
    'zope.security',
    'zope.securitypolicy',
    'zope.site',
    'zope.traversing',
    ]

setup(name=name,
      version=version,
      description='Grok components to include resources.',
      long_description=readme + '\n\n' + history,
      keywords='Grok resources fanstatic',
      author='Souheil Chelfouh',
      author_email='trollfot@gmail.com',
      url='http://pypi.python.org/pypi/megrok.resourceviewlet',
      download_url='http://pypi.python.org/pypi/megrok.resourceviewlet',
      license='ZPL 2.1',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['megrok'],
      include_package_data=True,
      platforms='Any',
      zip_safe=False,
      install_requires=[
          'fanstatic',
          'grokcore.viewlet',
          'setuptools',
          'zope.schema',
          'zope.viewlet',
          ],
      extras_require={'test': test_requires},
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Framework :: Zope3',
          'Intended Audience :: Other Audience',
          "License :: OSI Approved :: Zope Public License",
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          ],
      )
