from setuptools import setup, find_packages
import os

version = '0.6'

setup(name='nmd.plonelinkasvideoembed',
      version=version,
      description="Add a view plonelinkasvideoembed to display link content type as embed video by Makina Corpus",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='JeanMichel FRANCOIS',
      author_email='jeanmichel.francois@makina-corpus.com',
      url='http://svn.plone.org/svn/collective/nmd.plonelinkasvideoembed',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['nmd'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'p4a.videoembed'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,)
