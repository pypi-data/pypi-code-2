from setuptools import setup, find_packages
import os

version = '1.0.1'

setup(name='anz.cas',
      version=version,
      description="This is an Python implementation of the server-end of JA-SIG's CAS protocol.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone cas sso',
      author='jiangdongjin',
      author_email='eastxing@gmail.com',
      url='http://plone.org/products/anz.cas/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['anz'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'ZODB3>=3.8.3',
          'zope.proxy>=3.4.1',
          'zope.bforest',
          'uuid',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins = ["ZopeSkel"],
      )
