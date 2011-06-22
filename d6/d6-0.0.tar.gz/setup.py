#!/usr/bin/env python3

from distutils.core import setup
from d6._base import __version__, __doc__
from subprocess import check_output
from io import StringIO

def generate_changelog():
    """Create, read and return the Changelog"""
    log = check_output(["hg", "log", "--no-merges", "--template", "{tags} | - {desc}\n"])
    log = str(log, "utf-8")
    # strip out null tags
    l = ""
    tagged = 0
    for line in log.splitlines():
        if line.startswith(" | "):
            line = line.replace(" | ", "")
            l += line + "\n"
        else: # tag is a version
            if tagged > 1: break # get only the last version
            tag = line.split(" | ")[0]
            line = " | ".join(line.split(" | ")[1:])
            l += "\nd6 " + tag + "\n\n" + line + "\n"
            tagged += 1

    log = l

    return log

# Create the desription from the docstrings

DESCRIPTION = __doc__.split("\n")[0].split(" - ")[1:]

LONG_DESCRIPTION = "\n".join(__doc__.split("\n")[1:])

try:
    __changelog__ = generate_changelog()
    LONG_DESCRIPTION += "\n\n" + "Changes:" + "\n\n" +  __changelog__
except OSError: pass # hg not available

setup(name=__doc__.split("\n")[0].split(" - ")[0],
      version=__version__,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author='Arne Babenhauserheide',
      author_email='arne_bab@web.de',
      keywords=["ews", "rpg", "characters", "1d6", "d6"],
      license="GNU GPL-3 or later",
      platforms=["any"],
      requires = ["yaml"],
      classifiers = [
            "License :: OSI Approved :: GNU General Public License (GPL)",
            "Programming Language :: Python",
            "Operating System :: OS Independent",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Intended Audience :: Developers",
            "Intended Audience :: End Users/Desktop",
            "Environment :: Console",
            "Development Status :: 4 - Beta"
            ],
      url='http://1w6.org/programme',
      packages = ["d6"],
      scripts=["d6/char"]
     )
