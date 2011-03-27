#!/usr/bin/env python
#coding: utf-8

__author__ = "Alice"
__license__ = "GPL"
__version__ = "2.0.0"

from argparse import ArgumentParser
import src.cli as cli
import sys

DESCRIPTION = """ This script provide FTP client like Termainl. """
parser = ArgumentParser(description=DESCRIPTION,prog="ftpterm")

parser.add_argument("-v", "--version",  action="version",   version="%(prog)s : "+__version__ ,help="Show program version.")
parser.add_argument("-n", "--nomal",    action="store_true",dest="nomal",       help="Call nomal type. If you not write arg, run nomal type.")
parser.add_argument("-c", "--use-conf", action="store",     dest="config_file", help="Use config file.")
parser.add_argument("-u", "--upload",   action="store",     dest="opts",nargs=3,help="""Uplaod file. options : upload_file, config_file, filepath.""")

args = parser.parse_args()

if len(sys.argv[1:]) == 0:
	args.nomal = True

Launcher = cli.Parse_args(args)
