from setuptools import setup, find_packages
import os

name = "slapos.libnetworkcache"
version = '0.3'


def read(*rnames):
  return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


long_description = (
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
    )

setup(
    name=name,
    version=version,
    description="libnetworkcache - Client for ShaCache and ShaDir HTTP Server",
    long_description=long_description,
    license="GPLv3",
    keywords="slapos networkcache shadir shacache",
    install_requires=[
      'setuptools', # for namespace
    ],
    classifiers=[
      'Development Status :: 4 - Beta',
      'License :: OSI Approved :: GNU General Public License (GPL)',
      'Programming Language :: Python :: 2',
      ],
    zip_safe=True,
    packages=find_packages(),
    namespace_packages=['slapos'],
    test_suite="slapos.libnetworkcachetests"
    )
