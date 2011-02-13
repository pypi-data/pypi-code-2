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
# Instructions to use this script are below:
#
# Install the software by typing on the command line:
#    python setup.py install
#
# Command line for creating distributions:
#    python setup.py sdist --formats=gztar,zip bdist_rpm bdist_wininst
#
# Upload source packages to the Python Package Index:
#    python setup.py sdist --formats=gztar,zip upload
#
# Small overview of frequently used commands. The command line
# generally is:
#    python setup.py <command>  [--dry-run]
#
# Some commands are:
#    sdist         : create source distribution. (*.tar.gz or *.zip)
#    bdist_wininst : create Windows executable installer (binary distribution). (*.exe)
#    bdist_rpm     : create binary RPM distribution (*.rpm)
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


from distutils.core import setup
from ebstat import PROGRAM_VERSION


setup(
    name = 'JBidwatcher-Companion',
    version = PROGRAM_VERSION,
    author = 'Eike Welk',
    author_email = 'Eike.Welk@gmx.net',
    url = 'https://launchpad.net/jbidwatcher-companion',
    description = 'Price Statistics for Ebay - Use with JBidwatcher',
    long_description = \
'''A command line program that creates price vs. time graphs for completed 
auctions on Ebay. It is intended for use in conjunction with the Ebay bidding 
program JBidwatcher. 

JBidwatcher is available from: http://www.jbidwatcher.com

Dependencies
------------

The program needs the following libraries to run:

    * Numpy
    * Matplotlib
    * Dateutil
''',
    license = 'GPL',
    packages = [],
    scripts = ['ebstat.py'],
#      keywords = ["encoding", "i18n", "xml"],
#      platform = '',
#      download_url = '',
#      classifiers = [''],
    classifiers = [
        "Programming Language :: Python :: 2",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Topic :: Office/Business",
        ],      )

