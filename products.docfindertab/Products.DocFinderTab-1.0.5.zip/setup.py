from setuptools import setup, find_packages
from os.path import join

version = open(join("Products", "DocFinderTab", "version.txt")).read().strip()

setup(name='Products.DocFinderTab',
      version=version,
      description="Makes Dieter Maurer's DocFinder available from a ZMI management tab",
      long_description=open(join("Products", "DocFinderTab", "README.txt")).read() + '\n' +
                       open(join("Products", "DocFinderTab", "CHANGES.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Zope2",
        "Framework :: Plone",
        ],
      keywords='Zope2 DocFinder DocFinderTab',
      author='Stefan H. Holek',
      author_email='stefan@epy.co.at',
      url='http://plone.org/products/docfindertab',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      )
