from setuptools import setup, find_packages
from pkg_resources import resource_string
import os
import re
import sys

v = file(os.path.join(os.path.dirname(__file__), 'feed2mb', '__init__.py'))
VERSION = re.compile(r".*__version__ = '(.*?)'", re.S).match(v.read()).group(1)

setup(name='feed2mb',
      version=VERSION,
      description="Publish your feed items to a microblog",
      long_description=open('README').read(),
      classifiers=[
      "Intended Audience :: Developers",
      "Programming Language :: Python",
      "Environment :: Console",
      "Development Status :: 5 - Production/Stable"
      ],
      keywords='twitter feed identi.ca identica microblog wordpress',
      author='Walter Cruz',
      author_email='walter@waltercruz.com',
      url='http://bitbucket.org/waltercruz/feed2mb/',
      packages=['feed2mb','docs'],
      #package_data = {'docs':['*']},
      include_package_data=True,
      license='AGPL',
      zip_safe=False,
      scripts=['scripts/feed2mb'],
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
