from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='Products.Zope_Hotfix_20110622',
      version=version,
      long_description=open("README.txt").read() + "\n" +
                       open("HISTORY.txt").read(),
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Zope2",
        "License :: OSI Approved :: Zope Public License",
        ],
      keywords='security hotfix patch',
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.org',
      url='http://plone.org/products/plone-hotfix/releases/20110622',
      license='ZPL 2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      )
