from setuptools import setup, find_packages
import os

name = "slapos.tool.nosqltester_manager.kumo"
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
    author = 'Guillaume Bottex, for Nexedi',
    author_email = 'gbottex@tiolive.com',
    description = "Manager for Kumofs tester",
    license = "GPL",
    keywords = "kumofs test manager scheduler",
    classifiers=[
        "Framework :: Buildout",
        "Programming Language :: Python",
      ],
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    install_requires = ['Flask', 'slapos.tool.nosqltester_manager'],
    namespace_packages = ['slapos', 'slapos.tool', 'slapos.tool.nosqltester_manager'],
    entry_points = """
    [slapos.tool.nosqltester_manager.plugin]
    kumo=%s:KumoTesterManager
    """  % name,
    )
