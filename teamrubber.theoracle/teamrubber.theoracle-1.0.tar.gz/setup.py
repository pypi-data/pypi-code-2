from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='teamrubber.theoracle',
      version=version,
      description="Plone debug/development helper",
      long_description=open(os.path.join("docs", "README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Alan Hoey',
      author_email='alan.hoey@teamrubber.com',
      url='http://www.teamrubber.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['teamrubber'],
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
