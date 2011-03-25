import sys
from setuptools import setup, find_packages

version = '1.4.7'

if not '2.5' <= sys.version < '3.0':
    raise ImportError('Python version not supported')

tests_require = ['nose']

setup(name="Searchpy",
      version=version,
      install_requires=['mechanize >= 0.2.4', 'pyquery >= 0.6.1'],
      
      description="A google interface library",
      long_description="""\ SearchPy simplifies the process of
accessing search engine providers programmatically and also provides useful
tools..

It has a `mercurial repository
<https://ixmatus@bitbucket.org/ixmatus/searchpy>`_ that
you can install from with ``easy_install searchpy``

""",
      classifiers=["Intended Audience :: Developers",
                   "License :: OSI Approved :: Python Software Foundation License",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   ],
      author="Parnell Springmeyer",
      author_email="ixmatus@gmail.com",
      url="http://bitbucket.org/ixmatus/searchpy",
      license="PSF",
      zip_safe=False,
      packages=find_packages(),
      include_package_data=True,
      test_suite='nose.collector',
      tests_require=tests_require
      )
