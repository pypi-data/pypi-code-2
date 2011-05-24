from distutils.core import setup
setup(
    name = "vilib",
    packages = ["vilib"],
    version = "1.0.0",
    description = "A library to calculate the vegetation indices",
    author = "Sat Kumar Tomer",
    author_email = "satkumartomer@gmail.com",
    url = "http://ambhas.com/",
    download_url = "http://ambhas.com/tools/vilib-1.0.0.tar.gz",
    keywords = ["vegetation indices", "soil indices", "ndvi"],
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
A library to calculate the soil and vegetation indices. It can calculate the following indices:
-------------------------------------
 - RVI
 - NDVI
 - IPVI
 - DVI
 - RNDVI
 - MRVI
 - MPRI
 - SAVI
 - EVI2
 - MGNDVI
 - MNDVI
 - BI
 - RGRI 
 - GNDVI 
 - NDRGI   
 - NDVSI   
 - RDI  
 - TNDVI
 - GRVI  
 - OSAVI  
 - MGRVI
 - SLAVI
 - NDMI   
"""
)
