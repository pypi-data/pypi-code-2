from setuptools import setup

setup(
    name = "sake",
    packages = ["sake"],
    version = "0.0.1",
    install_requires = [
        "stacklesslib",
        "Paste",
        "PyYAML",
    ],
    description = "Enables easier Stackless Python application development",
    author = "Richard Tew",
    author_email = "richard.m.tew@gmail.com",
    url = "http://code.google.com/p/sake/",
    keywords = ["microthreads", "coroutines", "stackless",  "codereloading"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    long_description = """\
Sake
----

An easier way to create `Stackless Python`__ based applications.

__ http://www.stackless.com/

Stackless has a lot to offer, but it does so in a low-level and straightforward
manner.  Anyone who wishes to make use of it has to implement a lot of the same
supporting functionality, in order to get to the stage where they can implement
an application on top of it.  And then there is the domain knowledge that needs
to be factored into this supporting code, which may only be identified as
problems arise and are solved.

Sake aims to be a high-level framework that developers can take, and
immediately use to get started building an application.  All the standard
supporting logic that gets written, has been written.  Written within
`CCP Games`__, domain knowledge and corner cases learned over ten years of
Stackless usage has been taken into account.

__ http://www.ccpgames.com/
"""
)