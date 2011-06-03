# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: stefaan.himpe@gmail.com

from FactExtractor import FactExtractor

__author__="stefaan.himpe@gmail.com (aka: 'shi')" 
__date__ ="$Apr 10, 2011 11:20:21 PM$"
__version__="0.0.1"

def setup_argument_parsing():
    """
    Define command line options for our program.
    """
    import argparse
    import os
    parser = argparse.ArgumentParser(description="Process command line options")
    parser.add_argument('-s', '--sandbox', dest="sandbox", metavar="SANDBOX", type=str, default=".", help="generates intermediate files in the SANDBOX folder (if any)")
    parser.add_argument('-l', '--logfile', dest="logfile", metavar="LOGFILE", type=str, default="logfile.txt", help="choose how to name the logfile")
    parser.add_argument('-V', '--verbosity', dest="verbosity", metavar="VERBOSITY", type=int, default=30, help="choose log level (50 = CRITICAL, 40 = ERRROR, 30 = WARNING, 20 = INFO, 10 = DEBUG, 0 = NOT SET)")
    parser.add_argument('-r', '--report-name', dest="report", metavar="REPORTNAME", default="report.txt", type=str, help="generates a report with name REPORTNAME")
    parser.add_argument('-v', '--version', dest="version", action="store_true", help="show version and quit")

    parser.add_argument('-p', '--prefix-length', dest="prefixlength", type=int, default=2, help="max no of path prefixes to keep (to avoid duplicate names)")
    parser.add_argument('-i', '--case-insensitive', dest="case_insensitive", action="store_true", help="consider file names to be case insensitive (win32)")
    parser.add_argument('-I', '--include-dir', dest="include", metavar="INCLUDEDIR", default=[], type=str, action="append", help="add a directory to examine non-recursively")
    parser.add_argument('-R', '--recursive-include-dir', dest="recursive_include", metavar="RECURSIVEINCLUDEDIR", default=[], type=str, action="append", help="add a directory to examine recursively")
    parser.add_argument('-X', '--exclude-dir', dest="exclude", metavar="EXCLUDEDIR", default=[], type=str, action="append", help="exclude a directory from analysis")
    parser.add_argument('-Y', '--recursive-exclude-dir', dest="recursive_exclude", metavar="RECURSIVEEXCLUDEDIR", type=str, default=[], action="append", help="exclude a directory and all its subdirectories from analysis")
    parser.add_argument('-C', '--cppfile-suffix', dest="cppsuffix", default="cpp", type=str, action="store", help="define file extension of c/c++ files (default: cpp)")
    parser.add_argument('-H', '--headerfile-suffix', dest="headersuffix", default="h", type=str, action="store", help="define file extension of header files (default: h)")
    parser.add_argument('-S', '--path-separator', dest="separators", metavar="SEPARATOR", default=[os.sep], type=str, action="append", help="define an additional path separator (default: '%s')" % os.sep)
    parser.add_argument('-P', '--prolog-name', dest="prolog_name", metavar="PROLOGDATABASENAME", default="dependencies.pl", type=str, action="store", help="define the name of the prolog database that will be saved")
    parser.add_argument('-d', '--hierarchy-definition', dest="hierarchy", metavar="HIERARCHYDEFINITION", default="", type=str, action="store", help="location of hierarchy.txt (include constraint specificiation)")
    parser.add_argument('-f', '--common-root-folder', dest="common_root", metavar="COMMONROOTFOLDER", default=[], type=str, action="append", help="when displaying a file path, always start from the common root folder if possible")
    parser.add_argument('-c', '--strip-common-root-folder', dest="strip_common_root", action="store_true", help="when displaying a file path starting from a common root folder, include the common root folder from the displayed path")
    return parser

def setup_logging(options):
    """
    Set up default logging.
    """
    import logging
    from path import path
    p = path(options.logfile)
    folder_specified = p.dirname() != path('')
    if not folder_specified:
        p = path(options.sandbox)/p
    p = p.abspath()
    logging.basicConfig(filename="%s" % p, filemode='w', format='%(asctime)s # %(levelname)s # %(message)s', level=options.verbosity)

if __name__ == "__main__":
    options = setup_argument_parsing().parse_args()
    if options.version:
        print "PyCDep version %s. Program available under GPLv3 - copyright 2011 %s" % (__version__, __author__)
        import sys
        sys.exit(0)
    setup_logging(options)
    FX = FactExtractor(options)
    FX.run()
    
