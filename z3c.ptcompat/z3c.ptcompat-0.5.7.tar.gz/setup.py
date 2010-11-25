from setuptools import setup, find_packages
import sys, os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


version = '0.5.7'

tests_require = [
    'lxml',
    'z3c.pt',
    'zope.app.form',
    'zope.app.pagetemplate',
    'zope.app.publisher',
    'zope.tal',
    'zope.testing',
    'zope.viewlet',
    ],


setup(name='z3c.ptcompat',
      version=version,
      description="Compatibility-layer for Zope Page Template engines.",
      long_description=(
        ".. contents::\n\n" +
        read('README.txt')
        + "\n\n" +
        read('src', 'z3c', 'ptcompat', 'zcml.txt')
        + "\n\n" +
        read("CHANGES.txt")
        ),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zpt template zope',
      url='http://pypi.python.org/pypi/z3c.ptcompat',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      license='ZPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          ],
      extras_require = dict(
        zpt = ['zope.app.pagetemplate', 'zope.tal'],
        z3cpt = ['z3c.pt'],
        test = tests_require, # used by buildout.cfg testrunner
        ),
      tests_require = tests_require,
      test_suite="z3c.ptcompat.tests.test_doctests.test_suite",
      )
