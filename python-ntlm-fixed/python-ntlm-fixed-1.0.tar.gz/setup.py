from setuptools import setup, find_packages
import os
import sys

SRC_FOLDER = "src"

ENTRY_POINTS = { "console_scripts":[ "ntlm_example_simple=ntlm_examples.simple:main",
                                     "ntlm_example_extended=ntlm_examples.extended:main",] }

DEPENDANCIES = []

if sys.version_info < ( 2,5 ):
    DEPENDANCIES.append( "hashlib" )
    
setup(name='python-ntlm-fixed',
      version='1.0',
      description='Python library that provides NTLM support, including an authentication handler for urllib2 (with fixed hashlib dependency).',
      author='Matthijs Mullender',
      author_email='info@zopyx.com',
      url='http://pypi.python.org/pypi/python-ntlm-fixed',
      packages=["ntlm",],
      zip_safe=False,
      entry_points = ENTRY_POINTS,
      install_requires = DEPENDANCIES,
      )
