from setuptools import setup, find_packages
import sys, os

version = '1.1rc9'

tests_require = [
    'PIL',
    'Products.PloneTestCase',
    ]

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('docs', 'HISTORY.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('src', 'borg', 'project', 'README.txt')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n'
    )

setup(name='borg.project',
      version=version,
      description="Ability to create project workspaces with local workflow",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Plone project workspace teamspace',
      author='Martin Aspeli',
      author_email='optilude@gmx.net',
      url='http://svn.plone.org/svn/collective/borg/borg.project',
      license='GPL',
      packages=['borg', 'borg/project'],
      package_dir={'':'src'},
      namespace_packages=['borg'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          "borg.localrole>=1.1rc3",
          "Plone",
          "setuptools",
          "plone.app.content",
          "plone.contentrules", 
          "Products.CMFPlacefulWorkflow"
      ],
      extras_require=dict(tests=tests_require),
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
