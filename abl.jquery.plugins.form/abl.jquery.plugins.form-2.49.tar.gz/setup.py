from setuptools import setup, find_packages
import sys, os

version = '2.49'

setup(name='abl.jquery.plugins.form',
      version=version,
      description="ToscaWidgets wrapper for jquery.form.js",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='toscawidgets.widgets',
      author='Diez B. Roggisch',
      author_email='deets@web.de',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      package_data = {'': ['*.html', '*.txt', '*.rst']},
      namespace_packages = ['abl', 'abl.jquery', 'abl.jquery.plugins', 'abl.jquery.examples'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'abl.jquery',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
