from setuptools import setup, find_packages
import os

version = '0.1.2'

setup(name='mfabrik.plonezohointegration',
      version=version,
      description="Integration of Zoho web applications for Plone CMS",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='zoho plone crm integration',
      author='mFabrik Research Oy',
      author_email='research@mfabrik.com',
      url='http://webandmobile.mfabrik.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['mfabrik'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'mfabrik.zoho',
          'plone.app.z3cform',
          'plone.app.registry',
          'plone.directives.form'
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
