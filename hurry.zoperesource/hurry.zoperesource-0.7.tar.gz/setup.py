from setuptools import setup, find_packages
import sys, os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('src', 'hurry', 'zoperesource', 'README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )

setup(
    name='hurry.zoperesource',
    version='0.7',
    description="hurry.resource integration for Zope.",
    long_description=long_description,
    classifiers=['Framework :: Zope3'],
    keywords='',
    author='Martijn Faassen',
    author_email='faassen@startifact.com',
    url='http://pypi.python.org/pypi/hurry.zoperesource',
    license='ZPL',
    packages=find_packages('src'),
    namespace_packages=['hurry'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'grokcore.component',
        'hurry.resource >= 0.10',
        'z3c.autoinclude',
        'zope.app.publication',
        'zope.browserresource',
        'zope.component',
        'zope.interface',
        'zope.publisher',
        'zope.security',
        'zope.securitypolicy',
        'zope.traversing',
        ],
  extras_require = {
      'test': [
         'zope.testbrowser',
         'zope.app.authentication',
         'zope.app.testing',
         'zope.app.zcmlfiles',
         ],
      },
    entry_points={},
    )
