from distutils.core import setup
setup(
    name = "copulalib",
    packages = ["copulalib"],
    version = "1.0.0",
    description = "A library for the copula",
    author = "Sat Kumar Tomer",
    author_email = "satkumartomer@gmail.com",
    url = "http://ambhas.com/",
    download_url = "http://ambhas.com/tools/copulalib-1.0.0.tar.gz",
    keywords = ["copula", "bi-variate statistics"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        ],
    long_description = """ 
A library for the copula. It contains module for the following copula:
-------------------------------------
 - Frank
 - Clayton
 - Gumbel
"""
)
