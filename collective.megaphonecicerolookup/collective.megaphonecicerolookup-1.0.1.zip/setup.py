from setuptools import setup, find_packages
import os

version = '1.0.1'

setup(name='collective.megaphonecicerolookup',
      version=version,
      description="Megaphone plugin to look up elected officials based on address, via the Cicero API",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='megaphone petition letter plone legislator official geocoding',
      author='David Glick, Groundwire',
      author_email='davidglick@groundwire.org',
      url='http://svn.plone.org/svn/collective/collective.megaphonecicerolookup/trunk',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'collective.cicero',
          'collective.megaphone>=2.1b1',
          'plone.app.registry',
          'setuptools',
          'suds',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """
      )
