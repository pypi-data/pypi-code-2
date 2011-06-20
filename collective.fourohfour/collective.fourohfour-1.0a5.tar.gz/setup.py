from setuptools import setup, find_packages
import os

version = '1.0a5'

setup(name='collective.fourohfour',
      version=version,
      description="Aliasing of Plone content",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone fourohfour',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://pypi.python.org/pypi/collective.fourohfour',
      license='GPL',
      packages = find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.autopermission',
          'collective.testcaselayer',
          'plone.app.registry',
          'plone.directives.form',
          'Paste',
          'WebOb',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      
      [paste.filter_app_factory]
      handler = collective.fourohfour.middleware:make_handler
      """,
      )
