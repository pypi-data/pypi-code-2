import distribute_setup
distribute_setup.use_setuptools()

import os
from setuptools import setup, find_packages


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='buildboticon',
    version='0.2.0',
    author='Marcus Lindblom',
    author_email='macke@yar.nu',
    description=('A buildbot monitoring utility'),
    license='GPL 3.0',
    keywords='buildbot systemtray pyqt',

    url='http://bitbucket.org/marcusl/buildboticon',
    download_url='http://packages.python.org/buildboticon',

    package_dir={'':'src'},
    packages=find_packages('src', exclude=['*.tests']),
    long_description=read('README'),

    entry_points={
        'setuptools.installation': [
            'eggsecutable = bbicon.bbicon:main',
        ],
        'gui_scripts': [
            'buildboticon = bbicon.bbicon:main',
        ]
    },

    # we currently package icons as qt resources, so we're zip_safe
    zip_safe=True,

    test_suite='bbicon.tests',

    setup_requires=[
        'setuptools_hg',
    ],

    tests_require=[
        'unittest2 >= 0.5',
        'mock >= 0.7.0b4',
    ],

    install_requires=[
        'pyyaml >= 0.3',
#        'pyqt >= 4.7'   # PyQt doens't have anything useful on PyPi :(
    ],

    extras_require={
        'speech':  ['pyspeech >= 1.0'],
        'phidgets': ['PhidgetsPython >= 2.1.7'],
    },

    dependency_links=[
        'http://www.phidgets.com/programming_resources.php',
    ],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Desktop Environment',
        'License :: OSI Approved :: GNU General Public License (GPL)',
    ],
)
