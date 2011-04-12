from setuptools import setup, find_packages
import os

version = '0.1.0'

setup(name='experimental.collectionfix8463',
      version=version,
      description="A quick and dirty fix for the #8463 Plone issue with collections. USe only for versions before 3.3.6",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone skins bug template collection',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.net',
      url='http://svn.plone.org/svn/collective/experimental.collectionfix8463',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['experimental'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Plone<4.0dev',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
