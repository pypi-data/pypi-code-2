from distutils.core import setup
setup(
    name = "datalib",
    packages = ["datalib"],
    version = "0.0.0",
    description = "A library to work with time series data from xls",
    author = "Sat Kumar Tomer",
    author_email = "satkumartomer@gmail.com",
    url = "http://ambhas.com/",
    download_url = "http://ambhas.com/tools/datalib-0.0.0.tar.gz",
    keywords = ["time series", "xls"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        ],
    long_description=open('README.txt').read(),
)

