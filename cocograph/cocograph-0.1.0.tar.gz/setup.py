# -*- coding: utf-8 -*-
"""setup -- setuptools setup file for cocograph.
Tile Editor for Cocos2D & Pyglet
"""

__author__ = "Devon Scott-Tunkin(originator) Raymond Chandler III(forker)"
__author_email__ = "raymondchandleriii@gmail.com"
__version__ = "0.1.0"
__date__ = "2011 07 31"

try:
    import setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import setup, find_packages

f = open('README','rU')
long_description = f.read()
f.close()

setup(
    name = "cocograph",
    version = __version__,
    author = "cocograph",
    license="BSD",
    description = "A tile editor for cocos2d.",
    long_description=long_description,
    url = "https://github.com/kitanata/cocograph",
    download_url = "https://github.com/kitanata/cocograph/tarball/master",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        ("Topic :: Software Development :: Libraries :: Python Modules"),
        ("Topic :: Games/Entertainment"),
        ],
 
    packages = find_packages(),

    install_requires=['pyglet>=1.1.4', 'cocos2d>=0.4.0', 'kytten6>=6.0.0'],
    dependency_links=['http://code.google.com/p/pyglet/downloads/list',
                        'http://code.google.com/p/cocos2d/downloads/list',
                        'https://github.com/kitanata/Kytten'],

    include_package_data = True,
    zip_safe = False,
)
