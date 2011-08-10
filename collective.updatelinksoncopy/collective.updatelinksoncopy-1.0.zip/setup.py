from setuptools import setup, find_packages
import os

version = '1.0'

tests_require=[
    'ely.contentgenerator',
    'collective.testcaselayer',
    ]

setup(name='collective.updatelinksoncopy',
      version=version,
      description="Update links to child objects in TextFields and ReferenceFields when an Archetypes based object is copied and pasted",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "INSTALL.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
      keywords='Plone Archetypes',
      author='Matt Halstead',
      author_email='matt@elyt.com',
      url="http://plone.org/products/collective.updatelinksoncopy",
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      tests_require=tests_require,
      extras_require={'test': tests_require},
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
