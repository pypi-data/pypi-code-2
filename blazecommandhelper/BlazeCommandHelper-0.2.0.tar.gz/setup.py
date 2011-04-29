import os
import sys
from setuptools import setup, find_packages

cdir = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(cdir, 'readme.rst')).read()
CHANGELOG = open(os.path.join(cdir, 'changelog.rst')).read()

from blazech import __VERSION__

if sys.platform == 'win32':
    kw = dict(entry_points=dict(console_scripts=['bch=blazech:main']))
else:
    kw = dict(scripts=['scripts/bch'])

required_packages = ['BlazeUtils']
try:
    import argparse
except ImportError:
    required_packages.append('argparse')

setup(name='BlazeCommandHelper',
      version=__VERSION__,
      description="A framework that facilitates shell and batch scripting in Python",
      long_description=README + '\n\n' + CHANGELOG,
      classifiers=[
        'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
      ],
      author='Randy Syring',
      author_email='rsyring@gmail.com',
      url='http://bitbucket.org/rsyring/blazech/',
      license='BSD',
      packages=find_packages(),
      install_requires=required_packages,
      zip_safe=False,
      **kw)
