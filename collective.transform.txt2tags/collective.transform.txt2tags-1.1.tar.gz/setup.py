from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='collective.transform.txt2tags',
      version=version,
      description="txt2tags transform for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Plone transform',
      author='Ales Zabala Alava (Shagi)',
      author_email='shagi@gisa-elkartea.org',
      url='https://svn.plone.org/svn/collective/collective.transform.txt2tags',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.transform'],
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
