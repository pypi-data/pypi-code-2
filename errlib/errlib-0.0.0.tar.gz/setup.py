from distutils.core import setup
setup(
    name = "errlib",
    packages = ["errlib"],
    version = "0.0.0",
    description = "A library to estimate various error indices",
    author = "Sat Kumar Tomer",
    author_email = "satkumartomer@gmail.com",
    url = "http://ambhas.com/",
    download_url = "http://ambhas.com/tools/errlib-0.0.0.tar.gz",
    keywords = ["rmse", "correlation"],
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

