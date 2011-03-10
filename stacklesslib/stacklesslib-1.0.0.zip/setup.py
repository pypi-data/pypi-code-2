from setuptools import setup

setup(
    name = "stacklesslib",
    packages = ["stacklesslib"],
    version = "1.0.0",
    description = "Standard Stackless Python supporting functionality",
    author = "Richard Tew",
    author_email = "richard.m.tew@gmail.com",
    url = "http://code.google.com/p/sake/",
    keywords = ["microthreads", "coroutines", "stackless", "monkeypatching"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    long_description = """\
stacklesslib
============

This is a simple framework that layers useful functionality around the
Stackless scheduler.  It's sole purpose is to implement the logic that
an developer needs to implement themselves, to make best use of
Stackless.

 * A sleep function, to allow a tasklet to sleep for a period of time.
 * Monkeypatching to make blocking IO block tasklets not threads.
 """
)