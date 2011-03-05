from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

CPP_SOURCES = """./poly2tri/common/shapes.cc
./poly2tri/sweep/advancing_front.cc
./poly2tri/sweep/cdt.cc
./poly2tri/sweep/sweep.cc
./poly2tri/sweep/sweep_context.cc""".split("\n")

mod_math = Extension(
    "p2t",
    ["src/p2t.pyx"] + CPP_SOURCES,
    language = "c++"
)

setup(
    name = "poly2tri",
    version = "0.3",
    author = "mason.green",
    description = "A 2D constrained Delaunay triangulation library",
    url = "http://code.google.com/p/poly2tri/",

    cmdclass = {'build_ext': build_ext},
    ext_modules = [mod_math],
    install_requires = ["cython==0.14.1"],
)
