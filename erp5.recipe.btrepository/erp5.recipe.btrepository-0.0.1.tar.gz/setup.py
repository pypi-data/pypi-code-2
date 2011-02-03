from setuptools import setup, find_packages
import os

name = "erp5.recipe.btrepository"
version = '0.0.1'

def read(*rnames):
  return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description=( read('README.txt')
                   + '\n' +
                   read('CHANGES.txt')
                 )

setup(
  name = name,
  version = version,
  author = 'Rafael Monnerat',
  author_email = 'rafael@nexedi.com',
  description = 
    "zc.buildout recipe that creates an repository of business template",
  long_description = long_description,
  license = "ZPL 2.1",
  keywords = "bt5 erp5 buildout",
  classifiers = [
    "License :: OSI Approved :: Zope Public License",
    "Framework :: Buildout :: Recipe",
  ],

  package_dir = {'': 'src'},
  packages = find_packages('src'),
  namespace_packages = ['erp5', 'erp5.recipe'],
  include_package_data = True,
  install_requires = ['setuptools', 'zc.recipe.egg', "erp5.utils.dists"],
  entry_points = {'zc.buildout': ['default = %s:Recipe' % name]},
  tests_require=['zope.testing',],
  test_suite='%s.tests.test_suite' % name,
  )
