import os
from setuptools import setup, find_packages


setup(
    name='z3c.hashedresource',
    version='1.1.3',
    author='Wolfgang Schnerring',
    author_email='ws@gocept.com',
    description='Provides URLs for resources that change whenever their content changes.',
    url='http://pypi.python.org/pypi/z3c.hashedresource',
    long_description= (
        open(os.path.join('src', 'z3c', 'hashedresource', 'README.txt')).read()
        + '\n\n'
        + open('CHANGES.txt').read()),
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Framework :: Zope3'],
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['z3c'],
    install_requires=[
        'setuptools',
        'z3c.noop',
        # When using Zope3, we need zope.app.publisher>=3.8.2.
        'zope.app.publisher',
        'zope.component',
        'zope.interface',
        'zope.publisher',
        ],
    extras_require=dict(
        test=[
            'zope.app.testing',
            'zope.app.zcmlfiles',
            'zope.security',
            'zope.site',
            'zope.testbrowser',
        ]),
    include_package_data = True,
    zip_safe = False,
)
