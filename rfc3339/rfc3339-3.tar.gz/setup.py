try:
    from setuptools import setup
except:
    from distutils.core import setup
from os.path import join, dirname

import rfc3339

setup(name='rfc3339',
      version=rfc3339.__version__,
      py_modules=['rfc3339'],
      # metadata for upload to PyPI
      author=rfc3339.__author__,
      author_email=rfc3339.__author__,
      description=rfc3339.__doc__,
      long_description=rfc3339.__doc__,
      license=rfc3339.__license__,
      url='http://pypi.python.org/pypi/rfc3339/',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
          'Intended Audience :: End Users/Desktop',
          'Programming Language :: Python'])
