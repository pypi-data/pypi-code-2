import os, sys

from setuptools import setup, find_packages

version = '1.8'

def read(*rnames):
    return open(
        os.path.join('.', *rnames)
    ).read()

long_description = "\n\n".join(
    [read('README.txt'),
     read('docs', 'INSTALL.txt'),
     'Detailed documentation\n============================',
     read('src', 'collective', 'portlet', 'localcumulus', 'tests', 'renderer.txt'),
     read('src', 'collective', 'portlet', 'localcumulus', 'tests', 'custom.txt'),
     read('docs', 'HISTORY.txt'),
    ]
)

classifiers = [
    "Programming Language :: Python",
    "Topic :: Software Development",]

setup(
    name='collective.portlet.localcumulus',
    namespace_packages=['collective', 'collective.portlet',],
    version=version,
    description='Project collective.portlet.localcumulus cumulus product by Makina Corpus',
    long_description=long_description,
    classifiers=classifiers,
    keywords='',
    author='kiorky',
    author_email='kiorky@cryptelium.net',
    url='http://pypi.python.org/pypi/collective.portlet.localcumulus',
    license='GPL',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    install_requires=[
        'quintagroup.portlet.cumulus',
        'plone.memoize',
        'setuptools',
        'zope.interface',
        'zope.component',
        #'plone.reload',
        'zope.testing',
        # -*- Extra requirements: -*-
    ],
    extras_require={'test': ['IPython', 'zope.testing', 'mocker']},
    entry_points="""
    # -*- Entry points: -*-
    """,
)
# vim:set ft=python:
