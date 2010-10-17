from distutils.core import setup

from stats import __version__, __author__, __author_email__

setup(
    name = "stats",
    py_modules=["stats"],
    version = __version__,
    author = __author__,
    author_email = __author_email__,
    url = 'http://pypi.python.org/pypi/stats',
    keywords = ["statistics", "mathematics", "calculator"],
    description = "Statistical functions",
    long_description = """\
Statistical functions
---------------------

stats provides common statistics functions including:

- mean, median, mode
- geometric, harmonic and quadratic means
- variance and standard deviation (both for samples and populations)
- covariance and Pearson's correlation coefficient
- linear regression fitting
- plus others.


Requires Python 2.5, 2.6 or 2.7.
""",
    license = 'MIT',  # apologies for the American spelling
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Mathematics",
        "License :: OSI Approved :: MIT License",
        ],
    )

