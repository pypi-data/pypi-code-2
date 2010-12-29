from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='django-user_agent_detector',
      version=version,
      description="Detect and handle desktop vs mobile user agents with django-annoying",
      long_description="""\
Provides an easy way to specify Django templates for desktop browser use and mobile use for a view. Meant to marry django_annoying and minidetector""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='django django_annoying mobile iphone',
      author='Ryan Wilcox',
      author_email='rwilcox@wilcoxd.com',
      url='http://www.bitbucket.org/rwilcox/django-user_agent_detector',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
