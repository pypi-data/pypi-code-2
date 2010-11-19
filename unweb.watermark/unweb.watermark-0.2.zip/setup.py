from setuptools import setup, find_packages
import os

version = '0.2'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('docs/HISTORY.txt')
    + '\n' +
    read('docs/CONTRIBUTORS.txt')
    )


setup(name='unweb.watermark',
      version=version,
      description="Support for adding watermarks to images",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Multimedia :: Graphics",
        ],
      keywords='image photo watermark plone zope',
      author='unweb.me',
      author_email='we@unweb.me',
      url='http://svn.plone.org/svn/collective/unweb.watermark/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['unweb'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'archetypes.schemaextender',
          'plone.app.registry',
          'five.grok',
          'grokcore.view',
          'grokcore.viewlet',
          'grokcore.component',
          'martian',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
