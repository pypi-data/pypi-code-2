from setuptools import setup, find_packages
import os

version = '0.7'

setup(name='wow.armoryapi',
      version=version,
      description="Python World of Warcraft Armory API",
      long_description=open(os.path.join("docs", "HISTORY.txt")).read() + "\n" +
                       open(os.path.join("wow", "armoryapi", "README.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='armory api wow warcraft',
      author='Marc Goetz',
      author_email='goetz.marc@googlemail.com',
      url='http://code.google.com/p/wowarmoryapi/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['wow'],
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
