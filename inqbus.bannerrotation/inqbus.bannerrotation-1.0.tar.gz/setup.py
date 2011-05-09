from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='inqbus.bannerrotation',
      version=version,
      description="A simple, ajax based bannerrotation viewlet for plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='ajax banner rotation viewlet plone',
      author='Max Brauer',
      author_email='max.brauer@inqbus.de',
      url='http://inqbus-hosting.de/community',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['inqbus'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.browserlayer',
          'z3c.form',
          'plone.z3cform',
          'plone.app.z3cform',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
