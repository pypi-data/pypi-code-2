from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='googl',
      version=version,
      description="Goo.gl API wrapper for Python.",
      long_description="""\
A goo.gl api wrapper for Python.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='goo.gl url shortener',
      author='Douglas Camata',
      author_email='d.camata@gmail.com',
      url='blog.douglascamata.net',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
            'restfulie',
            'ludibrio',
            'should-dsl',
            'specloud',
            'pinocchio',
            'google-api-python-client'
          # -*- Extra requirements: -*-
      ],
      dependency_links = ['https://github.com/caelum/restfulie-py/tarball/master#egg=restfulie-dev',
                          'http://darcs.idyll.org/~t/projects/pinocchio-latest.tar.gz',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

