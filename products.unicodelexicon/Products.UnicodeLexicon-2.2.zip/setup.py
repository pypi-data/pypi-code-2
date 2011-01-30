# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = '2.2'

setup(name='Products.UnicodeLexicon',
      version=version,
      description="Unicode aware lexicon for ZCTextIndex",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Zope2',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
      ],
      keywords='unicode zctextindex',
      author='Stefan H. Holek',
      author_email='stefan@epy.co.at',
      url='http://pypi.python.org/pypi/Products.UnicodeLexicon',
      license='BSD',
      packages=find_packages(),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
      ],
)
