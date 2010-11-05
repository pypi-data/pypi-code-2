from setuptools import setup, find_packages
import sys, os

version = '0.1.1'

setup(name='metals',
      version=version,
      description="list metadata for (movie) files on the command line",
      long_description="""Please see <http://code.google.com/p/metals/>""",
      classifiers=[
        'Development Status :: 4 - Beta', 
        'Environment :: Console', 
        'Intended Audience :: Education', 
        'License :: OSI Approved :: MIT License', 
        'Operating System :: POSIX :: Linux', 
        'Programming Language :: Python', 
        'Topic :: Documentation', 
        'Topic :: Utilities'], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='metadata imdb ls',
      author='David',
      author_email='dayf@gmx.net',
      url='http://code.google.com/p/metals/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=['sqlalchemy', 'imdbpy', 'termcolor'],
      entry_points="""
      # -*- Entry points: -*-
      """,
      scripts = ['metals.sh']
      )
