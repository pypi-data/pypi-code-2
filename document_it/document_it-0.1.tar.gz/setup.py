import os
from setuptools import setup

try:
    here = os.path.dirname(os.path.abspath(__file__))
    description = file(os.path.join(here, 'README.txt')).read()
except IOError:
    description = None

version = '0.1'

deps = ['Markdown']

setup(name='document_it',
      version=version,
      description="mirror text documentation to MDN",
      long_description=description,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='mozilla',
      author='Jeff Hammel',
      author_email='jhammel@mozilla.com',
      url='http://k0s.org/mozilla/hg/DocumentIt',
      license='MPL',
      py_modules=['document_it'],
      packages=[],
      include_package_data=True,
      zip_safe=False,
      install_requires=deps,
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      document-it = document_it:main
      """,
      )

