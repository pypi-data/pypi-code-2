import os
from setuptools import setup


f = open('README')
try:
    README = f.read()
finally:
    f.close()


setup(name='pypi2rpm', version='0.5.1', author='Tarek Ziade',
      author_email='tarek@ziade.org',
      description='Script that transforms a sdist archive '
                  'into a rpm archive',
      long_description=README,
      url='http://bitbucket.org/tarek/pypi2rpm',
      packages=['pypi2rpm', 'pypi2rpm.command'],
      scripts=['pypi2rpm/pypi2rpm.py'],
      install_requires=['Distutils2', 'argparse'])
