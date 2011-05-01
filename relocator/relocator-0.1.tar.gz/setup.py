from setuptools import setup, find_packages

try:
    description = file('README.txt').read()
except IOError: 
    description = ''

version = "0.1"

setup(name='relocator',
      version=version,
      description="change Location field in responses using WSGI middleware",
      long_description=description,
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      author='Jeff Hammel',
      author_email='jhammel@mozilla.com',
      url='',
      license="MPL",
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
         'WebOb',	
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
      
