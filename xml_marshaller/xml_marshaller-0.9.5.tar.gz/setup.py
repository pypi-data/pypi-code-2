# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

name = 'xml_marshaller'
version = '0.9.5'

def read(name):
    return open(name).read()

long_description=(
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
    )

setup(name=name,
      version=version,
      description="Converting Python objects to XML and back again.",
      long_description=long_description,
      classifiers=['Development Status :: 4 - Beta',
             'Intended Audience :: Developers',
             'License :: OSI Approved :: Python License (CNRI Python License)',
             'Operating System :: OS Independent',
             'Topic :: Text Processing :: Markup :: XML'], 
      keywords='XML marshaller',
      author='XML-SIG',
      author_email='xml-sig@python.org',
      maintainer='Nicolas Delaby',
      maintainer_email='nicolas@nexedi.com',
      url='http://www.python.org/community/sigs/current/xml-sig/',
      license='Python License (CNRI Python License)',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=['lxml',],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
