from setuptools import setup, find_packages
import os

version = '0.3'

setup(name='anthill.customexport',
      version=version,
      description="Makes it possible to export custom folder contents (from portal_skins/custom and portal_view_customizations) to filesystem",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zope patch customfolder skinning theme skin plone',
      author='Simon Pamies',
      author_email='s.pamies@banality.de',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['anthill'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
