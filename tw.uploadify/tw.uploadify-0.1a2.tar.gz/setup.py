import os
import sys

from setuptools import setup, find_packages

execfile(os.path.join("tw", "uploadify", "release.py"))

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    '\n.. contents::\n\n' +
    'Detailed Documentation\n' +
    '**********************\n'
    + '\n' +
    read('README.txt')
    + '\n' +
    'Change history\n' +
    '**************\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n'
    )

setup(
    name=__DISTRIBUTION__,
    version=__VERSION__,
    description=__DESCRIPTION__,
    author=__AUTHOR__,
    author_email=__EMAIL__,
    url=__URL__,
    install_requires=[
        "ToscaWidgets",
        ## Add other requirements here
        "tw.jquery",
        "tw.forms",
        ],
    packages=find_packages(exclude=['ez_setup', 'tests']),
    namespace_packages = ['tw'],
    zip_safe=False,
    include_package_data=True,
    test_suite = 'nose.collector',
    entry_points="""
        [toscawidgets.widgets]
        # Register your widgets so they can be listed in the WidgetBrowser
        widgets = tw.uploadify
        samples = tw.uploadify.samples
    """,
    keywords = [
        'toscawidgets.widgets', 'jquery','uploadify','progress bar'
    ],
    long_description=long_description,
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Environment :: Web Environment :: ToscaWidgets',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Widget Sets',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: TurboGears :: Widgets',
        'License :: OSI Approved :: MIT License',
    ],
)
