from setuptools import setup, find_packages
import os

name = "slapos.tool.nosqltester"
version = '0.0.4'

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
    description = "NoSQL systems tester",
    license = "GPL",
    keywords = "nosql test",
    classifiers=[
        "Framework :: Buildout",
        "Programming Language :: Python",
      ],
    packages = find_packages('src'),
    package_dir = {'':'src'},
    install_requires = ['Flask'],
    namespace_packages = ['slapos', 'slapos.tool'],
    entry_points = """
    [console_scripts]
    nosqltester = %s:main
    """  % name,
    )
