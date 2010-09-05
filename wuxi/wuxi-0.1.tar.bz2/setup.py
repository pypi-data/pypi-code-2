# -*- coding: utf-8 -*-
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

import re
version_rx = r"^__version__ = '(.*)'$"
version_pattern = re.compile(version_rx)


fd = open('wuxi/__init__.py')
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

print "running setup for wuxi version %s" % __version__


requires = ['sphinx', 'liberet']


setup(
    name="wuxi",
    version=__version__,
    description="Django template bridge and themes for Sphinx",
    author="worrp",
    author_email = "contact@worrp.com",
    classifiers=["Development Status :: 1 - Planning",
                "Intended Audience :: Developers",
                "License :: OSI Approved :: BSD License",
                "Programming Language :: Python",
                "Framework :: Django",
                "Intended Audience :: Developers",
                "Topic :: Documentation",
                "Topic :: Software Development :: Documentation",
                ],
    url="http://bitbucket.org/worrp/wuxi",
    license="BSD",
    download_url="http://pypi.python.org/packages/source/w/wuxi/wuxi-%s.tar.gz" % __version__,
    packages=find_packages(),
    install_requires=requires,
      )
    
