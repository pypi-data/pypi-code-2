from setuptools import setup, find_packages
import os

version = '0.5'

setup(name='pleiades.transliteration',
      version=version,
      description="Transliteration of names from various writing systems to our modern Roman writing system following conventions of the Pleiades Project.",
      long_description=open("README.txt").read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='ancient language greek latin transliteration',
      author='Tom Elliot',
      author_email='tom.elliott@nyu.edu',
      url='',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pleiades'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
