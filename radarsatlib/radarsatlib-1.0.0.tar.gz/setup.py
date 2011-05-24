from distutils.core import setup
setup(
    name = "radarsatlib",
    packages = ["radarsatlib"],
    version = "1.0.0",
    description = "A library to process, calibrate and filter the RADARSAT-2 data",
    author = "Sat Kumar Tomer",
    author_email = "satkumartomer@gmail.com",
    url = "http://ambhas.com/",
    download_url = "http://ambhas.com/tools/radarsatlib-1.0.0.tar.gz",
    keywords = ["radarsat-2", "backscatter", "filter"],
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
A library to work with the RADARSAT-2 data. It can do the following processing on the data:
-------------------------------------
 - sinclair matrix
 - sigma-nought
 - filtering
 - change resolution of the data
"""
)
