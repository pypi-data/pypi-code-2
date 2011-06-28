# -*- coding: utf-8 -*-
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

import re
version_rx = r"^__version__ = '(.*)'$"
version_pattern = re.compile(version_rx)


fd = open('dubbel.py')
try:
    for line in fd:
        m = version_pattern.match(line)
        if m:
            break
    else:
        raise Exception("couldn't find __version__")
finally:
    fd.close()

__version__ = m.group(1)

print "running setup for dubbel version %s" % __version__

requires = ['pyyaml']


setup(
        name="dubbel",
        version=__version__,
        description="ConfigParser/YAML hybrid",
        author="Walter Wefft",
        author_email = "contact@worrp.com",
        classifiers=["Development Status :: 4 - Beta",
                    "Intended Audience :: Developers",
                    "License :: OSI Approved :: BSD License",
                    "Programming Language :: Python",
                    "Topic :: Software Development :: Libraries",
                    "Topic :: Software Development :: Libraries :: Python Modules",
                    ],
        url="http://wefft.codebasehq.com/python/dubbel",
        license="BSD",
        download_url="http://pypi.python.org/packages/source/d/dubbel/dubbel-%s.tar.gz" % __version__,
        py_modules=['dubbel'],
        install_requires=requires,
)
    
