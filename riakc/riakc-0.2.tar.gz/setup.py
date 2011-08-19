import sys
from setuptools import setup, find_packages

version = '0.2'

if not '2.5' <= sys.version < '3.0':
    raise ImportError('Python version not supported')

tests_require = ['nose']

setup(name="riakc",
      version=version,
      install_requires=['cmdln', 'protobuf', 'riak'],
      
      description="A simple riak commandline client",
      classifiers=["Intended Audience :: Developers",
                   "License :: OSI Approved :: Python Software Foundation License",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   ],
      author="Parnell Springmeyer",
      author_email="ixmatus@gmail.com",
      url="http://bitbucket.org/ixmatus/riakc",
      license="PSF",
      zip_safe=True,
      packages=find_packages(),
      include_package_data=True,
      test_suite='nose.collector',
      tests_require=tests_require
      )
