from distutils.core import setup
from piratebay import __version__

setup(
    name="piratebay",
    version=__version__,
    description="A python interface to thepiratebay dot org.",
    license="MIT/X",
    url="http://hg.sobber.org/piratebay",
    long_description="A python interface to thepiratebay dot org.",
    packages=["piratebay"]
)