from setuptools import setup, find_packages
import sys, os

version = '0.4.1'

setup(name='formtags',
      version=version,
      description="python library to generate forms and validate them using formencode and sqlalchemy",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Michael van Tellingen',
      author_email='michaelvantellingen@gmail.com',
      url='http://code.google.com/p/py-formtags/',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
