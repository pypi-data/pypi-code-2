from setuptools import setup, find_packages
import os

version = '2.0b1'

setup(name='collective.subtractiveworkflow',
      version=version,
      description="The DCWorkflow giveth and the SubtractiveWorkflow taketh away.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone zope cmf workflow permissions',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://pypi.python.org/pypi/collective.subtractiveworkflow',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'rwproperty',
          'zope.interface',
          'zope.component',
          'Products.CMFCore',
          'Products.DCWorkflow',
          'Products.GenericSetup',
      ],
      entry_points="""
      """,
      )
