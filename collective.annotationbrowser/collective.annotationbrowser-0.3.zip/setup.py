from setuptools import setup, find_packages
import os

version = '0.3'

tests_require = ['collective.testcaselayer']

setup(name='collective.annotationbrowser',
      version=version,
      description="Browser/editor for Zope annotations",
      long_description=open("README.txt").read() + "\n\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone zope annotations',
      author='Radim Novotny',
      author_email='novotny.radim@gmail.com',
      url='http://plone.org',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir = {'':'src'},
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      tests_require=tests_require,
      extras_require={'tests': tests_require},
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
