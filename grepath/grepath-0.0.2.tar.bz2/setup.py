import os
import sys

from distutils.core import setup

def read_file(relpath):
    return open(os.path.join(os.path.dirname(__file__), relpath)).read()

_readme_lines = read_file("README.txt").splitlines()

#XXX tests, docs, *.bat on Windows, no extension on Linux
CLASSIFIERS = """\
Development Status :: 2 - Pre-Alpha
Environment :: Console
Intended Audience :: Developers
Intended Audience :: End Users/Desktop
Intended Audience :: System Administrators
License :: OSI Approved :: MIT License
Operating System :: Microsoft :: Windows
Operating System :: POSIX :: Linux
Programming Language :: Python :: 2
Topic :: Software Development :: Libraries :: Python Modules
Topic :: System :: Systems Administration
Topic :: Utilities
"""

NAME             = 'grepath'
VERSION          = '0.0.2'
DESCRIPTION      = _readme_lines[0]
LONG_DESCRIPTION = "\n".join(_readme_lines[2:])
URL              = "http://gist.github.com/79233"
LICENSE          = 'MIT'
CLASSIFIERS      = filter(len, CLASSIFIERS.split('\n'))
AUTHOR           = "zed"
AUTHOR_EMAIL     = "arn.zart+zed@gmail.com"
PLATFORMS        = ["Windows", "Linux"]


if 'posix' in sys.builtin_module_names:
    script_name = NAME
else: # nt, os2, ce
    script_name = NAME+".py"


if __name__=="__main__":
    setup(
        name=NAME,
        version=VERSION,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        url=URL,
        license=LICENSE,
        classifiers=CLASSIFIERS,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        platforms=PLATFORMS,
        py_modules=[NAME],
        scripts=[script_name],
        )

