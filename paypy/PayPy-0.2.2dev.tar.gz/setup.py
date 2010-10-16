import sys
from setuptools import setup

version = '0.2.2'

if not '2.5' <= sys.version < '3.0':
    raise ImportError('Python version not supported')

tests_require = ['nose']

setup(name="PayPy",
      version=version,
      install_requires=['ElementTree >= 1.2.7'],
#      requires_python='>=2.5,<3', # PEP345
      description="Payment gateway API integration package",
      long_description="""\
Paypy simplifies payment gateway interaction by homogenizing the 
programming interface for multiple providers.

It has a `mercurial repository
<https://ixmatus@bitbucket.org/ixmatus/paypy>`_ that
you can install from with ``easy_install paypy==dev``

""",
      classifiers=["Intended Audience :: Developers",
                   "License :: OSI Approved :: Python Software Foundation License",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   ],
      author="Parnell Springmeyer",
      author_email="ixmatus@gmail.com",
      url="http://bitbucket.org/ixmatus/paypy",
      license="PSF",
      zip_safe=False,
      packages=["paypy"],
      include_package_data=True,
      test_suite='nose.collector',
      tests_require=tests_require
      )
