import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.3'

long_description = (
    read('README.txt')
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Change history\n'
    '==============\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Download\n'
    '========\n'
    )

setup(name='django-cachepurge',
      version=version,
      description='''Django Middleware and utilities that send "PURGE" request to an upstream cache''',
      long_description=long_description,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'Topic :: Internet :: Proxy Servers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='django cache squid varnish',
      author='Bertrand Mathieu',
      author_email='bert.mathieu@gmail.com',
      url='http://launchpad.net/django-cachepurge',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
