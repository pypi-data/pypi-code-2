from setuptools import setup, find_packages
import os

version = '0.7'

setup(name='collective.viewlet.references',
      version=version,
      description="Viewlet that shows all the references to the current article including back references",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone collective viewlet references details',
      author='David Jonas',
      author_email='david@v2.nl',
      url='https://svn.v2.nl/plone/collective.viewlet.references',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.viewlet'],
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
