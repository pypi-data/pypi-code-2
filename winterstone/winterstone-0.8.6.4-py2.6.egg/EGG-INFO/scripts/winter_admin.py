#!/usr/bin/python
# -*- coding: utf-8 -*-
# Winterstone admin

__author__ = 'Averrin'
__version__ = '0.2'

import argparse
import os
import shutil
import winter_project
from winterstone.snowflake import replaceInFile

def main():
    parser = argparse.ArgumentParser(description='Winterstone admin')
#    parser.add_argument('integers', metavar='N', type=int, nargs='+',
#                       help='an integer for the accumulator')
    parser.add_argument('new', help='create new app')
    parser.add_argument('appname', help='name of new app')
    parser.add_argument('-v','--version', action='version', version='%(prog)s 0.1')

    args = parser.parse_args()
    try:
        dst=os.path.join(os.getcwd(),args.appname)
        shutil.copytree(winter_project.__path__[0],dst,ignore=shutil.ignore_patterns('*.pyc', 'tmp*'))
        replaceInFile(os.path.join(args.appname,'config/main.cfg'),'%TITLE%',args.appname)
    except OSError:
        print 'Dir "%s" already exists' % args.appname



if __name__ == '__main__':
    main()
