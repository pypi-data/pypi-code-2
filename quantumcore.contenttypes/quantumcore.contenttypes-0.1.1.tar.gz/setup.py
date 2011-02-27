from setuptools import setup, find_packages
import os

version = '0.1.1'

setup(name='quantumcore.contenttypes',
      version=version,
      description="A content type detection library using the freedesktop shared mime database",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='mimetypes mimetype contenttype magic detection types freedesktop sharedmime mime quantumcore',
      author='Christian Scholz',
      author_email='cs@comlounge.net',
      url='http://quantumcore.org/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['quantumcore'],
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
