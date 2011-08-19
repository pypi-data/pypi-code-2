import sys
from setuptools import find_packages

try:
    from setuptools import setup
    kw = {'entry_points':
          """[console_scripts]\nriakc = riakc:main\n""",
          'zip_safe': False}
except ImportError:
    from distutils.core import setup
    if sys.platform == 'win32':
        print('Note: without Setuptools installed you will have to use "python -m riakc ENV"')
        kw = {}
    else:
        kw = {'scripts': ['scripts/riakc']}

version = '0.3.6'

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
      py_modules=['riakc'],
      packages=find_packages(),
      include_package_data=True,
      test_suite='nose.collector',
      tests_require=tests_require,
      **kw
      )
