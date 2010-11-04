from setuptools import setup, find_packages
import os

version = '0.1'

readme_filename = os.path.join('src', 'megrok', 'nozodb', 'README.txt')
long_description = open(readme_filename).read() + '\n\n' + \
                   open(os.path.join('docs', 'HISTORY.txt')).read()

test_requires = ['zope.app.wsgi',]

setup(name='megrok.nozodb',
      version=version,
      description="This package allows you to run grok without the zodb",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='grok wsgi zodb',
      author='Christian Klinger',
      author_email='cklinger@novareto.de',
      url='http://pypi.python.org/pypi',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['megrok'],
      include_package_data=True,
      zip_safe=False,
      extras_require={'test': test_requires},
      install_requires=[
          'setuptools',
          'grok',
          # -*- Extra requirements: -*-
      ],
      entry_points={
         'paste.app_factory': [
            'nozodb = megrok.nozodb:nozodb_factory',
            ]
      }
      )
