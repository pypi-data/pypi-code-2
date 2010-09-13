from setuptools import setup, find_packages
import os

version = '0.3'

setup(name='wow.activityapi',
      version=version,
      description="Python World of Warcraft Activity API",
      long_description=open(os.path.join("docs", "HISTORY.txt")).read() + "\n" +
                       open(os.path.join("wow" , "activityapi", "README.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='activity activities feed api wow warcraft',
      author='Marc Goetz',
      author_email='goetz.marc@googlemail.com',
      url='http://code.google.com/p/wowactivityapi/',
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
