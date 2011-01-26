from setuptools import setup, find_packages
import os

version = '2.6.6.1'

setup(name='Products.FCKeditor',
      version=version,
      description="FCKeditor.Plone",
      long_description=open(os.path.join("docs", "LASTCHANGES.txt")).read() + "\n\n" +
                       open("README.txt").read() + "\n\n" +
                       open(os.path.join("docs", "FAQ.txt")).read() + "\n\n" +
                       open(os.path.join("docs", "TODO.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope plone wysiwyg editor',
      author='Ingeniweb',
      author_email='support@ingeniweb.com',
      url='http://plone.org/products/fckeditor',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
