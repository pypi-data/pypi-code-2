from setuptools import setup, find_packages
import os

version = '1.0.0'

setup(name='monet.calendar.star',
      version=version,
      description="A complete and modular site calendar application for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone plonegov calendar event monet',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.net',
      url='http://plone.org/products/monet.calendar.star',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['monet', 'monet.calendar'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'monet.calendar.event',
          'monet.calendar.extensions'
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
