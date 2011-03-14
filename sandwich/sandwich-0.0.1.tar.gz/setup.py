__author__="Rob O'Dwyer"

from setuptools import setup,find_packages

setup (
    name = 'sandwich',
    version = '0.0.1',
    packages = find_packages(),
    zip_safe = True,

    author = 'Rob O\'Dwyer',
    author_email = 'odwyerrob@gmail.com',

    url = 'http://doteight.com/',
    license = 'MIT',
    description = 'sudo make me a sandwich.',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Natural Language :: English',
        'Topic :: Utilities',
    ],

    entry_points = {
        'console_scripts': [
            'make_me_a_sandwich = sandwich:main',
        ],
        'gui_scripts': []
    }
)

