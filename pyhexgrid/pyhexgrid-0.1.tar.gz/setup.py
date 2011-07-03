# Setup script for python module.

from distutils.core import setup
from hexgrid import __version__, __url__

with open('README') as fp:
    readme = fp.read()

setup(name             = "pyhexgrid",
      author           = "Glenn Hutchings",
      author_email     = "zondo42@gmail.com",
      description      = "Tool for managing hexagonal grids.",
      long_description = readme,
      url              = __url__,
      version          = __version__,
      license          = "GPL",
      packages         = ["hexgrid"])
