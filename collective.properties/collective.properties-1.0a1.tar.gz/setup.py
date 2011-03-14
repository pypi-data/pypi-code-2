from setuptools import setup, find_packages
import os

version = '1.0a1'

setup(name='collective.properties',
      version=version,
      description="Provides form to update object properties via Plone UI.",
      long_description=open("README.txt").read() + "\n" +
          open(os.path.join("collective", "properties", "TODO.txt")).read(
              ) + "\n" +
          open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='plone properties form ui',
      author='Vitaliy Podoba',
      author_email='vitaliypodoba@gmail.com',
      url='http://svn.plone.org/svn/collective/collective.properties',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.z3cform',
      ],
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
