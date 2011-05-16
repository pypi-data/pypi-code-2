from setuptools import setup, find_packages
import os

version = '0.1-alpha-3'

setup(name='five.taskqueue',
      version=version,
      description="Zope2 integration of z3c.taskqueue",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['five'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'z3c.taskqueue',
          'five.dbevent',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
