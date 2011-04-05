from setuptools import setup, find_packages
import os

version = '0.2.1'

setup(name='zettwerk.i18nduder',
      version=version,
      description="A helper/wrapper script for i18ndude to easier working with translation files in a common plone environment.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone, i18ndude',
      author='zettwerk GmbH',
      author_email='jk@zettwerk.com',
      url='http://zettwerk.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zettwerk'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'i18ndude'
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      duder = zettwerk.i18nduder.duder:main
      """,
      )
