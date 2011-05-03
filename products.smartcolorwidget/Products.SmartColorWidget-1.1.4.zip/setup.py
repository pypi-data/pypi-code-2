from setuptools import setup, find_packages
import os

def _textFromPath(*names):
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, *names)
    return open(path, 'r').read().strip()

version = _textFromPath('Products', 'SmartColorWidget', 'version.txt')

long_description = '\n\n'.join(
    (_textFromPath('README.txt'), _textFromPath('docs', 'HISTORY.txt'))
     )

setup(name='Products.SmartColorWidget',
      version=version,
      description="Smart color picker widget for Archetypes",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='plone widget colorpicker',
      author='Ingeniweb',
      author_email='support@ingeniweb.com',
      url='http://plone.org/products/smartcolorwidget',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'plone.browserlayer',
          ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
