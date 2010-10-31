from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.1'

long_description = (
    read('README.txt')
    + '\n' +
    'Contributors\n'
    '~~~~~~~~~~~~\n'
    + '\n' +
    read('docs/CONTRIBUTORS.txt')
    + '\n' +
    read('docs/HISTORY.txt')
    + '\n' +
   'Download\n'
   '--------\n'
    )

setup(name='collective.piwik.now',
      version=version,
      description="A portlet that uses the Piwik open source analytics system to display how many people are using your Plone site at the moment",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.piwik'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
