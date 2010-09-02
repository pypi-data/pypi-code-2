from setuptools import setup, find_packages
import os

version = open(os.path.join("sc","base","cdn","version.txt")).read()

setup(name='sc.base.cdn',
      version=version,
      description="",
      long_description=open(os.path.join("sc","base","cdn","README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        ],
      keywords='cdn web plone distribution',
      author='Simples Consultoria',
      author_email='products@simplesconsultoria.com.br',
      url='http://www.simplesconsultoria.com.br/',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['sc', 'sc.base'],
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
