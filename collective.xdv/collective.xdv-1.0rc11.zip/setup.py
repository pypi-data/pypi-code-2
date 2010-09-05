from setuptools import setup, find_packages
import os

version = '1.0rc11'

setup(name='collective.xdv',
      version=version,
      description="Integrates the xdv Deliverance implementation with Plone using a post-publication hook to transform content",
      long_description=open("README.txt").read() + "\n\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone xdv deliverance theme transform xslt',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://pypi.python.org/pypi/collective.xdv',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'xdv>=0.3rc1',
          'lxml>=2.2.4',
          'plone.app.registry>=1.0a2',
          'plone.subrequest',
          'plone.transformchain',
          'repoze.xmliter',
          'five.globalrequest',
      ],
      extras_require={
          'Zope2.10': ['ZPublisherEventsBackport',
                       'collective.directoryresourcepatch'],
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
