version = '0.13.1'

import os
from setuptools import setup, find_packages


setup(
    name='z3c.recipe.compattest',
    version = version,
    author='Grok Contributors',
    author_email='grok-dev@zope.org',
    description='Buildout recipe to create testrunners for testing compatibility with other packages',
    url='http://pypi.python.org/pypi/z3c.recipe.compattest',
    long_description= (
        '.. contents::'
        + '\n\n'
        + open('CHANGES.txt').read()
        + '\n\n'
        '======================\n'
        'Detailed Documentation\n'
        '======================'
        + '\n\n' +
        open(os.path.join(
            'src', 'z3c', 'recipe', 'compattest', 'README.txt')).read()),
    keywords = "zope3 setuptools egg kgs",
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Framework :: Zope3'],
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['z3c', 'z3c.recipe'],
    install_requires=[
        'setuptools',
        'zc.buildout >= 1.5.1',
        'zc.recipe.testrunner >= 1.4.0',
        ],
    # zope.dottedname is just used as a dummy package to demonstrate things
    # with, it's not actually imported
    extras_require=dict(test=[
          'zope.dottedname',
          'zope.testing',
        ]),
    entry_points = {
        'zc.buildout': ['default = z3c.recipe.compattest.recipe:Recipe'],
        },
    include_package_data = True,
    zip_safe = False,
)
