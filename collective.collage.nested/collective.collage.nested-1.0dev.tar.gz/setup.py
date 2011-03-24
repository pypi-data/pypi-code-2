from setuptools import setup, find_packages
import os

version = '1.0dev'

setup(name='collective.collage.nested',
      version=version,
      description="Display a nested Collage inside Collage",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "AUTHORS.txt")).read() + "\n" + 
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Marcos F. Romero',
      author_email='marcos.romero {at} inter-cultura {dot} com',
      url='http://svn.plone.org/svn/collective/Products.Collage/addons/collective.collage.nested/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.collage'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Products.Collage',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
