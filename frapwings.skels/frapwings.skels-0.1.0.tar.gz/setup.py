from setuptools import setup, find_packages
import os

version = '0.1.0'
README = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()
CHANGES = open(os.path.join(os.path.dirname(__file__), 'CHANGES.txt')).read()
long_description = README + '\n\n' + CHANGES + '\n\n'

setup(
    name='frapwings.skels',
    version=version,
    description='This package is the frapwings skelton package.',
    long_description=long_description,
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='frapwings skels skelton',
    author='kazuya kawaguchi',
    author_email='kawakazu80@gmail.com',
    url='http://d.hatena.ne.jp/kazu_pon/',
    license='LGPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['frapwings'],
    include_package_data=True,
    test_suite='nose.collector',
    test_requires=['Nose'],  
    zip_safe=False,
    exclude_package_data={
        '': ['.gitignore'], 'images': ['*.xcf', '*.blend']
    },
    setup_requires=[
        'setuptools_git >= 0.3', 
    ],
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        #'PasteScript',
        #'Cheetah',
    ],
    entry_points="""
    # -*- Entry points: -*-
    [paste.paster_create_template]
    frapwings_package = frapwings.skels.package:Package
    """,
)
