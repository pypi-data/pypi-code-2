from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='unimr.memcachedlock',
      version=version,
      description="Memcached based locking factory functions to provide shared locking (e.g. bet. zeo-clients)",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='ZEO Zope Memcached Lock',
      author='Andreas Gabriel',
      author_email='gabriel@hrz.uni-marburg.de',
      url='https://svn.plone.org/svn/collective/unimr.memcachedlock',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['unimr'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'lovely.memcached',
          'collective.monkeypatcher',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
