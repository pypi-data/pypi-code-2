from setuptools import setup, find_packages
import sys,os

version = '0.1'

tests_require = [
    'pytest',
    'zope.app.appsetup',
    'zope.app.zcmlfiles',
    'zope.browserpage',
    'zope.securitypolicy',
    'infrae.testbrowser',
    ]

docs_require = tests_require + [
    'Sphinx',
    'docutils',
    'roman',
    ]

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read(os.path.join('README.txt'))
    + '\n' +
    read(os.path.join('CHANGES.txt'))
    + '\n' +
    'Download\n'
    '********\n'
    )

setup(name='zope.pytest',
      version=version,
      description="zope pytest integration",
      long_description=long_description,
      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Programming Language :: Python",
        "Framework :: Zope3",
        ],
      keywords='',
      author='Martijn Faassen and contributors',
      author_email='zope-dev at zope dot org',
      url='http://pypi.python.org/pypi/zope.pytest',
      license='ZPL',
      packages=find_packages('src',exclude=['ez_setup']),
      namespace_packages=['zope'],
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.configuration',
          'zope.component',
          'zope.testing',
          'zope.event',
          'zope.processlifetime',
          'zope.app.publication',
          'zope.app.wsgi',
          'ZODB3',
          'WebOb',
          'simplejson'
          # -*- Extra requirements: -*-
      ],
      extras_require={
        'tests': tests_require,
        'docs': docs_require,
        },
      entry_points={
      }
      )
