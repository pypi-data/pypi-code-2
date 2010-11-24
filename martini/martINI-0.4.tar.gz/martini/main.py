#!/usr/bin/env python

"""
main front-end functions for command-line programs
"""

import config
import os
import sys
from optparse import OptionParser

sep = '--' # section separator

def parse_args(*args):
    """
    convert command line options to files, sections, and options
    returns a tuple:
    ( [files], { 'section': { 'option': 'value', 'option2': 'value2' } } )
    """

    # find the files
    # XXX note this prohibits files starting with --
    index = None
    for index, value in enumerate(args):
        if value.startswith(sep):
            break
    else:
        return (args, [])

    files = args[:index]
    args = args[index:]

    # find the sections
    ini = []
    for arg in args:
        if arg.startswith(sep):
            arg = arg[len(sep):]
            assert arg
            section = []
            ini.append((arg, section))
        else:
            section.append(arg)

    return (files, ini)

def parse_options(*args):
    files, sections = parse_args(*args)
    ini = {}
    for section, options in sections:
        ini[section] = {}
        for option in options:
            key, value = option.split('=', 1)
            ini[section][key] = value

    return (files, ini)

def set(args=None):

    usage = "%s file1 [file2] [...] --section1 option1=value1 option2=value2 --section2 option3=value3"
    
    # process arguments
    if args is None:
        args = sys.argv[1:]
    files, sections = parse_options(*args)

    # display usage information
    if not files:
        print 'Usage:'
        print usage % os.path.basename(sys.argv[0])
        sys.exit(0)

    # process the files
    for f in files:
        if f == '-':
            fp = sys.stdin
        else:
            fp = file(f)
        munger = config.ConfigMunger(fp, sections)

        if f == '-':
            fp = sys.stdout
        else:
            fp.close()
            fp = file(f, "w")
        munger.write(fp=fp)
       
def get(args=None):

    usage = "%s file1 [file2] [...] --section1 option1 option2 --section2 option3"

    # process arguments
    if args is None:
        args = sys.argv[1:]
    files, sections = parse_args(*args)

    # display usage information
    if not files:
        print 'Usage:'
        print usage % os.path.basename(sys.argv[0])
        sys.exit(0)

    # process the files
    for f in files:
        if f == '-':
            fp = sys.stdin
        else:
            fp = file(f)
        munger = config.ConfigMunger(fp)
        for section, options in sections:
            if section in munger.sections():
                if options:
                    for option in options:
                        value = munger.get(section, option)
                        if value is not None:
                            print value
                else:
                    config.ConfigMunger({section: munger[section]}).write()

def delete(args=None):

    usage = "%s file1 [file2] [...] --section1 option1 option2 --section2 option3"

    # process arguments
    if args is None:
        args = sys.argv[1:]
    files, sections = parse_args(*args)

    # display usage information
    if not files:
        print 'Usage:'
        print usage % os.path.basename(sys.argv[0])
        sys.exit(0)

    # process the files
    for f in files:
        if f == '-':
            fp = sys.stdin
        else:
            fp = file(f)
        conf = config.ConfigMunger(fp).dict()
        for section, options in sections:
            if section in conf:
                if options:
                    for option in options:
                        if option in conf[section]:
                            conf[section].pop(option)
                else:
                    conf.pop(section)
        if f == '-':
            fp = sys.stdout
        else:
            fp.close()
            fp = file(f, 'w')
        config.ConfigMunger(conf).write(fp)

def munge(args=None):

    usage = "%s file1 [file2] [...]"

    # process arguments
    if args is None:
        args = sys.argv[1:]

    parser = OptionParser()
    parser.add_option('-O', dest='output',
                      help="name of file to output (stdout if not specified)")
    options, args = parser.parse_args(args)
    files, sections = parse_options(*args)

    # display usage information
    if not files:
        print 'Usage:'
        print usage % os.path.basename(sys.argv[0])
        sys.exit(0)

    # munge the files
    conf = list(files) 
    conf.append(sections)
    munger = config.ConfigMunger(*conf)
    if options.output:
        fp = file(options.output, 'w')
    else:
        fp = sys.stdout
    munger.write(fp)
 
if __name__ == '__main__':
    set(sys.argv[1:])
