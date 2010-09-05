#!/usr/bin/env python

from distutils.core import setup

setup(name         = "PyTap",
      version      = "0.1.1",
      description  = "Object-oriented wrapper around Linux TUN/TAP device",
      author       = "Dominik George",
      author_email = "dev@naturalnik.de",
      url          = "http://www.launchpad.net/pytap",
      packages     = ["pytap"],
      package_dir  = {"": "src"},
      requires     = ["fcntl", "struct", "os", "atexit"]
     )
