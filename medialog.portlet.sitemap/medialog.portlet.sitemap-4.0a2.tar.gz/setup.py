from setuptools import setup, find_packages
import os

version = '4.0a2'

setup(name='medialog.portlet.sitemap',
      version=version,
      description="Shows the whole sitemap in a portlet. For Plone 4",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Espen Moe-NIlssen',
      author_email='espen@medialog.no',
      url='http://medialog.no',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['medialog', 'medialog.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
