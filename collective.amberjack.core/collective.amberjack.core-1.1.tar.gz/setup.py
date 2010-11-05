from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='collective.amberjack.core',
      version=version,
      description="The Amberjack layer",
      long_description=open(os.path.join("collective/amberjack/core", "README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read() + "\n" +
                       open(os.path.join("docs", "AUTHORS.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Zope2",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Massimo Azzolini and contributors',
      author_email='collective.amberjack.support@lists.coactivate.org',
      url='http://pypi.python.org/pypi/collective.amberjack.core',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.amberjack'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.layout',
          'Products.GenericSetup',
          'collective.js.jqueryui>=1.8dev',
          'i18ndude',
          'plone.registry',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      [console_scripts]
      i18ndude_aj=collective.amberjack.core.translation.script:main
      """,
      )
