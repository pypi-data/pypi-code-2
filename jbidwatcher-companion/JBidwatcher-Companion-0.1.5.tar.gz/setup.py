# -*- coding: utf-8 -*-
############################################################################
#    Copyright (C) 2011 - 2011 by Eike Welk                                       #
#    eike.welk@gmx.net                                                     #
#                                                                          #
#    This program is free software; you can redistribute it and#or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################


#                Setup script for Bidwatcher Companion
# -----------------------------------------------------------------------------
# Instructions to use this script:
#
# Install the software by typing on the command line:
#    python setup.py install
#
# Command line for creating packages:
#    python setup.py sdist --formats=gztar,zip bdist_rpm bdist_egg bdist_wininst
#
# Upload packages to the Python Package Index:
#    python setup.py register
#    python setup.py sdist --formats=gztar,zip bdist_egg upload
#    rm ~/.pypirc
#
#
# Small overview of frequently used commands. The command line
# generally is:
#    python setup.py <command>  [--dry-run]
#
# Some commands are:
#    sdist         : create source distribution. (*.tar.gz or *.zip)
#    bdist_wininst : create Windows executable installer (binary distribution). (*.exe)
#    bdist_rpm     : create RPM (*.rpm) packages, binary and source
#    bdist_egg     : create an *.egg package
#    install       : install the software
#    upload        : upload packages to the Python Package Index
#    --dry-run     : test the operation without doing anything
#
# also useful:
#    python setup.py --help
#    python setup.py --help-commands
#
#
# IMPORTANT:
# Files for the source distribution are also specified in the file:
#    MANIFEST.in


#TODO: When porting to Python3, mention the additional command:
#         check         : test the installation script

from setuptools import setup
#from distutils.core import setup
from ebstat import PROGRAM_VERSION


setup(
    name = 'JBidwatcher-Companion',
    version = PROGRAM_VERSION,
    author = 'Eike Welk',
    author_email = 'Eike.Welk@gmx.net',
    url = 'https://launchpad.net/jbidwatcher-companion',
    description = 'Price Statistics for Ebay - Use with JBidwatcher',
    long_description = \
'''A command line program (`ebstat.py`) that creates price vs. time graphs for
completed auctions on Ebay. It is intended for use in conjunction with the Ebay
bidding program JBidwatcher. 

JBidwatcher is available from: http://www.jbidwatcher.com


Dependencies
------------

This program is written in the **Python** programming language, and needs a
Python interpreter to run. Additionally it uses the following Python libraries: 

    - **Numpy** for numerical computations (http://numpy.scipy.org/)
    - **Matplotlib** for the graph window (http://matplotlib.sourceforge.net/)

**Windows** users should install **Python XY**, a (giant) Python distribution 
for scientists. This is the most easy way for them to install all dependencies 
at once.

    http://www.pythonxy.com/
    
**Linux** users need to use their distribution's installation program(s) to
install the dependencies. *Numpy* and *Matplotlib* are packaged for most 
Linux distributions.


Installation
------------

JBidwatcher-Companion can be installed with the program **easy_install**,
which downloads the necessary package from the Pyhon Package Index
(http://pypi.python.org/pypi), and installs it.   

Get administrative priviliges, then open a **shell window** / **DOS box** 
and type: ::

    easy_install jbidwatcher-companion

    
Usage
-----

To get help on the available options, type: ::

    ebstat.py -h
    
List the tabs in JBidwatcher's database: ::

    ebstat.py ls
    
Create a graph of the (finished) auctions in the tab `Nikon SB`, the moving 
median is computed over 40 days: ::

    ebstat.py gr -t "Nikon SB" -w 40


For more information on installation and usage see **README.txt** in the 
source packages, and here:

    http://packages.python.org/JBidwatcher-Companion/


Report Bugs
-----------

Bugs and feature requests (wishlist) can be reported on the development website
here:

    https://bugs.launchpad.net/jbidwatcher-companion
''',
    license = 'GPL',
    packages = [],
    scripts = ['ebstat.py'],
    install_requires = ['numpy', 'matplotlib'],
#      keywords = ['Ebay'],
#      platform = '',
#      download_url = '',
    classifiers = [
        "Programming Language :: Python :: 2",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Topic :: Office/Business",
        ],      )

