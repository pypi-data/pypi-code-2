from setuptools import setup, find_packages
import sys, os

version = '0.2.1'

setup(name='wsgitemplates',
      version=version,
      description="A series of templates for use in creating WSGI applications",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='wsgi template paste',
      author='Matthew Wilkes',
      author_email='matt@matthewwilkes.name',
      url='http://code.google.com/p/wsgitemplates',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'PasteScript',
        'Cheetah>=1.0',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      [paste.paster_create_template]
      wsgi_package = wsgitemplates:Package

      wsgi_filter = wsgitemplates:Middleware
      wsgi_composite = wsgitemplates:Composite
      wsgi_application = wsgitemplates:EndPoint
      """,
      )
