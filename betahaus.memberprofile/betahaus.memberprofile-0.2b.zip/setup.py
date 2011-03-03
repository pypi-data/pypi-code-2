from setuptools import setup, find_packages
import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.2b'
name='betahaus.memberprofile'

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '==============\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Known Issues\n'
    '============\n'
    + '\n' +
    read('KNOWN_ISSUES.txt')

    )

setup(name='betahaus.memberprofile',
      version=version,
      description="Flexible member profiles for Plone",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone',
      author='Robin Harms Oredsson, Martin Lundwall et.al.',
      author_email='robin@betahaus.net',
      url='http://pypi.python.org/pypi/betahaus.memberprofile',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['betahaus'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'archetypes.memberdatastorage',
          'Plone',
      ],
      extras_require={
          'test': ['plone.app.testing',]
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
