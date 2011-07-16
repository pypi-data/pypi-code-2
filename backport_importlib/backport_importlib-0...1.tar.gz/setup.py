
import os
from importlib import import_module
from distutils.core import setup, Extension


# required data
name = "backport_importlib"
package_name = name
summary = "A script to backport the full importlib to 2.x"

# dymanically generated data
pypi_url = "http://pypi.python.org/pypi?name=%s&:action=display" % name
home_page = "https://bitbucket.org/ericsnowcurrently/%s/" % name
version = import_module(package_name).__version__
version = ".".join(str(val) for val in version)
description = """\
Introduced in Python 3.1, the importlib package provides a pure Python
implementation of the import machinery.  It is also available on PyPI
as a [very] watered down backport.

The backport_importlib package provides a script that will backport the
full importlib package to 2.x.  Keep in mind that the backport is quite
naive and likely incomplete.  However, it passes the rudimentary tests
included in the script.

The script is optparse-based and the "-h" flag should be sufficient to
see how to use it.  For information on how to use importlib, please
refer to the current 3.x stdlib documentation.  The script will update
the importlib modules in-place, and will not install importlib for you.
Also, you have to provide your own copy of the 3.x importlib, which you
can get from hg.python.org/cpython (under Lib).

If you find cases where the backport could be improved please let me
know.  Also, it probably won't work for Python earlier than 2.4, so
keep that in mind.

One last thing.  A big reason that importlib was not released on PyPI
as a full backport was to encourage adoption of 3.x.  I stand with
Brett on that choice.  This tool is meant for the desparate only.  In
truth, importlib provides very little that you don't already have in
the 2.x import machinery, so if you think you need it you're probably
wrong."""

# set up packages

exclude_dirs = [
        ]

packages = []
for path, dirs, files in os.walk(package_name):
    if "__init__.py" not in files:
        continue
    path = path.split(os.sep)
    if path[-1] in exclude_dirs:
        continue
    packages.append(".".join(path))


# other data

classifiers = [
        #"Development Status :: 1 - Planning",
        #"Development Status :: 2 - Pre-Alpha",
        #"Development Status :: 3 - Alpha",
        "Development Status :: 4 - Beta",
        #"Development Status :: 5 - Production/Stable",
        #"Development Status :: 6 - Mature",
        #"Development Status :: 7 - Inactive",
        "Intended Audience :: Developers",
        #"License :: OSI Approved :: Apache Software License",
        #"License :: OSI Approved :: BSD License",
        #"License :: OSI Approved :: MIT License",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        #"Programming Language :: Python :: 3.2",
        #"Programming Language :: Python :: 3.3",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
        ]


if __name__ == "__main__":
    setup (
            name=name,
            version=version,
            author="Eric Snow",
            author_email="ericsnowcurrently@gmail.com",
            url=home_page,
            #license="New BSD License",
            description=summary,
            long_description=description,
            classifiers=classifiers,
            packages=packages,
            )
