import os
from setuptools import setup
from setuptools.command.sdist import sdist as _sdist
from setuptools import find_packages
import sys

class sdist(_sdist):

    def run(self):
        """ Override to barf is we can't import setuptools_bzr.
        """
        try:
            import setuptools_bzr
        except ImportError:
            print >> sys.stderr, "No setuptools_bzr intalled, aborting."
            sys.exit(1)
        _sdist.run(self)

here = os.path.abspath(os.path.dirname(__file__))
package = os.path.join(here, 'Products/Zelenium')

def _package_doc(name):
    f = open(os.path.join(package, name))
    return f.read()

_boundary = '\n\n'
LONG_DESC = ( open('README.txt').read()
         + _boundary
         + open('CHANGES.txt').read()
         + _boundary
         )

setup(name='Products.Zelenium',
      version=_package_doc('version.txt').strip(),
      description='Run Selenium test suites from within Zope2',
      long_description=LONG_DESC,
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Zope2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Testing",
        ],
      keywords='selenium zope2',
      author="Tres Seaver",
      author_email="tseaver@palladion.com",
      url="http://pypi.python.org/pypi/Products.Zelenium",
      license="ZPL 2.1",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['Products'],
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Zope2 >= 2.9.8',
      ],
      test_suite='Products.Zelenium.tests',
      entry_points="""
      [zope2.initialize]
      Products.Zelenium = Products.Zelenium:initialize
      """,
      cmdclass={'sdist': sdist},
      )
