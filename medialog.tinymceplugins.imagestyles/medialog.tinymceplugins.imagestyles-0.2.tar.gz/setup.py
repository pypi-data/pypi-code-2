from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='medialog.tinymceplugins.imagestyles',
      version=version,
      description="A TinyMCE plugin for having more styles (classes) for images",
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
