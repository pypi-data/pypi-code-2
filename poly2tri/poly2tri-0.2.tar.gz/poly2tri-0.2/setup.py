from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

from imports import CPP_SOURCES

mod_math = Extension(
    "p2t",
    ["src/p2t.pyx"] + CPP_SOURCES,
    language = "c++"
)

setup(
    name = "poly2tri",
    version = "0.2",
    cmdclass = {'build_ext': build_ext},
    ext_modules = [mod_math],
    install_requires = ["cython==0.14.1"],
)
