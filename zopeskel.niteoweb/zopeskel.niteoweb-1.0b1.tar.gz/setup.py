from setuptools import setup, find_packages
import os

version = '1.0b1'

setup(name='zopeskel.niteoweb',
      version=version,
      description="Paster templates for standard NiteoWeb Plone projects",
      long_description=open("README.txt").read() +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        ],
      keywords='plone zopeskel',
      author='NiteoWeb Ltd.',
      author_email='info@niteoweb.com',
      url='http://pypi.python.org/pypi/zopeskel.niteoweb',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zopeskel'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'PasteScript',
          'ZopeSkel',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.paster_create_template]
      niteoweb_project = zopeskel.niteoweb.niteoweb:NiteoWeb
      """,
      )
