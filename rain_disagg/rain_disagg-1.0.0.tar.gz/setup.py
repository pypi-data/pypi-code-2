from distutils.core import setup
setup(
    name = "rain_disagg",
    packages = ["rain_disagg"],
    version = "1.0.0",
    description = "A library to disaggregate the rainfall",
    author = "Sat Kumar Tomer",
    author_email = "satkumartomer@gmail.com",
    url = "http://ambhas.com/",
    download_url = "http://ambhas.com/tools/rain_disagg-1.0.0.tar.gz",
    keywords = ["rainfall", "disaggregation", "daily to hourly"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        ],
    long_description = """ 
A library to disaggregate the rainfall. It uses the random multipicative cascade
moethod. The approach is given in the following article:
    Sat Kumar, M. Sekhar, D. V. Reddy. Improving the disaggregation of daily 
    rainfall into hourly rainfall using hourly soil moisture
"""
)
