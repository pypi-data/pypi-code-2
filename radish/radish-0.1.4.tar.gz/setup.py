from distutils.core import setup

setup(
    name = "radish",
    packages = ["radish"],
    package_data={'radish': ['features/*.*']},
    version = "0.1.4",
    description = "A set of common tools for testing django projects with lettuce.",
    author = "Red Interactive",
    author_email = "geeks@ff0000.com",
    url = "http://ff0000.com/",
    download_url = "https://github.com/ff0000/radish",
    keywords = ["django", "admin", "bdd", "tdd", "documentation", "lettuce"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "Natural Language :: English",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Testing",
        "Topic :: Utilities"
        ],
    long_description = """\
A set of common tools for testing django projects with lettuce.
-------------------------------------

This module adds a set of step definitions to lettuce (http://www.lettuce.it)
implementing the most common actions that a user can perform through a browser
(such as navigating, clicking, filling forms).

The goal is to make Django developers integrate lettuce features in their code
more rapidly, since they do not have to write the step definitions, which are
included in this module.
"""
)

# To create the package: python setup.py register sdist upload