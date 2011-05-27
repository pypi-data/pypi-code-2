from setuptools import setup, find_packages
version = '3.0'
name = "slapos.rebootstrap"

setup(
  name=name,
  version=version,
  description="A zc.buildout extension to solve chicken-and-egg problem of"\
      " using python which is built by itself",
  long_description=open("README.txt").read() + "\n\n" +
    open("CHANGES.txt").read(),
  classifiers=[
      "Development Status :: 4 - Beta",
      "Framework :: Buildout :: Extension",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: Zope Public License",
      "Programming Language :: Python",
      "Topic :: Software Development :: Build Tools",
      "Topic :: Software Development :: Libraries :: Python Modules",
      ],
  entry_points={
     'zc.buildout.extension': ['extension = %s:extension' % name],
     },
  license='ZPL 2.1',
  include_package_data=True,
  namespace_packages=['slapos'],
  packages=find_packages(),
  zip_safe=True,
  install_requires=[
    'setuptools',
    'zc.buildout'
    ],
  tests_require=[
      'zope.testing',
    ],
  test_suite='%s.tests.test_suite' % name,
)
