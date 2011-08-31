from setuptools import setup, find_packages
import os

version = '0.1.0'

setup(name='collective.rtvideo.metacafe',
      version=version,
      description="The Metacafe Plone support for RedTurtle Video",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
      keywords='plone plonegov video embed metacafe',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.net',
      url='http://plone.org/products/redturtle.video',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.rtvideo'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'redturtle.video>=0.6.0',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
