from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='collective.contentrules.template',
      version=version,
      description="A Plone content rule for creating content based on templates",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone content rules template',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://pypi.python.org/pypi/collective.contentrules.template',
      maintainer='Luciano Pacheco',
      maintainer_email='lucmult@gmail.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.contentrules'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.contentrules',
          'plone.contentrules',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
