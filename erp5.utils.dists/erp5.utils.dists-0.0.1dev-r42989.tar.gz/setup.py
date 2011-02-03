from setuptools import setup, find_packages
import os

name = "erp5.utils.dists"
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
    "This library aims to provide utility scripts to manipulate BT5 compress"\
    " and repositories creation.",
  long_description = long_description,
  license = "GPLv3",
  keywords = "erp5 bt5 distribute",
  classifiers = [
    "Topic :: Utilities",
    "Topic :: System :: Archiving :: Packaging",
  ],

  package_dir = {'': 'src'},
  packages = find_packages('src'),
  namespace_packages = ['erp5', 'erp5.utils'],
  include_package_data = True,
  install_requires = [],
  entry_points = {
     'console_scripts' : [
         'bt5_repository_builder = erp5.utils.dists:download_repository_builder',
         'bt5_genlist = erp5.utils.dists:generate_bt5_list',
         'bt5_build_from_folder = erp5.utils.dists:local_repository_builder' ]
    }
  )
