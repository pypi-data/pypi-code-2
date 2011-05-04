from setuptools import setup, find_packages
import os

version = '0.0.1'

setup(name='medialog.tinymceplugins.imagestyles',
      version=version,
      description="An not so advanced TinyMCE plugin for handling links to galleries",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Plone",
        "Programming Language :: Python",
        "Programming Language :: JavaScript",
        ],
      keywords='tinymce plugin image styles',
      author='Espen Moe-Nilssen',
      author_email='espen@medialog.no',
      url='http://svn.plone.org/svn/collective/medialog.tinymceplugins.imagestyles/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['medialog', 'medialog.tinymceplugins'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.TinyMCE',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
