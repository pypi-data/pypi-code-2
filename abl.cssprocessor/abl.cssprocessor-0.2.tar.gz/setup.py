import os
import sys
from setuptools import setup, find_packages

setup(
    name="abl.cssprocessor",
    version="0.2",
    description="A processor to aggregate CSS-files and their referenced media",
    author="Diez B. Roggisch",
    author_email="diez.roggisch@ableton.com",
    url="",
    license="MIT",
    download_url='',
    install_requires=[
        "pyparsing",
        "abl.vpath>=0.4",
        "argparse",
        ],
    packages=find_packages(exclude=['ez_setup', 'tests']),
    namespace_packages = ['abl', ],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Environment :: Web Environment :: ToscaWidgets',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Widget Sets',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    entry_points= {

        "console_scripts": [
            "css_validator = abl.cssprocessor.validator:validator",
            ]
        }
)
