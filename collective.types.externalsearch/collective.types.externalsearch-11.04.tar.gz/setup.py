from setuptools import setup, find_packages
import os

version = open(os.path.join("collective", "types", "externalsearch", "version.txt")).read().strip()

setup(name='collective.types.externalsearch',
      version=version,
      description="External searches in Plone",
      long_description="""\
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone types search google',
      author='Liz Dahlstrom',
      author_email='lhill2@u.washington.edu',
      url='http://svn.plone.org/svn/collective/collective.types.externalsearch/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.types'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.DataGridField>1.5',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=[],
      )
