from setuptools import setup, find_packages
import os

version = '1.5'

setup(name='archetypes.multifile',
      version=version,
      description="This package adds a field to upload multiple files",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone archetypes multi file field',
      author='Matous Hora',
      author_email='matous.hora@dms4u.cz',
      url='http://pypi.python.org/pypi/collective.multifile',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['archetypes'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      """,
      paster_plugins = ["ZopeSkel"],
      )
