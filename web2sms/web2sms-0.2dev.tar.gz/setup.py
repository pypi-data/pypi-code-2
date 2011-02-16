from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='web2sms',
      version=version,
      description="A python client for Cosmote web2sms service.",
      long_description=open(os.path.join(os.path.dirname(__file__), "README.rst")).read(),
      classifiers=[
      "Development Status :: 4 - Beta",
      "Topic :: Communications :: Telephony",
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers

      keywords='sms api cosmote greece mobile client',
      author='Kostas Papadimitriou',
      author_email='vinilios@gmail.com',
      url='http://www.bitbucket.org/vinilios',
      license="GNU LGPL",
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "httplib2"
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
