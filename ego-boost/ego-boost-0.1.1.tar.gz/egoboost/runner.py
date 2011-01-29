# This file is part of the egoboost package which is release under the MIT
# License. You can find the full text of the license in the LICENSE file.
# Copyright (C) 2010 Sebastian Rahlf <basti at redtoad dot de>

import cmd
import glob
import os, os.path
import optparse
import re
import simplejson
import sys

import storage
import utils

CONFIG_DIR = os.path.expanduser('~/.ego-boost')
DATABASE = 'downloads.db'

class CommandLineInterpreter (cmd.Cmd):

    """
    Line-oriented command interpreter.
    """

    prompt = '> '

    def __init__(self, db):
        cmd.Cmd.__init__(self)
        self.db = db
        self.stop = False

    def default(self, line):
        print 'Unknown command %r!' % line

    def get_names(self):
        names = cmd.Cmd.get_names(self)
        return names + [attr for attr in dir(self) if attr.startswith('do_')]

    def do_EOF(self, line):
        self.stop = True
        return True

    def do_quit(self, line):
        """
        Exit command line.
        """
        return self.do_EOF(line)

    def postloop(self):
        print 'Bye.'
    
    def register(self, name, cls):
        """
        Registers a command.
        """
        #print 'Register command %s to %r.' % (name, cls)
        func = cls(self.db)
        func.__doc__ = cls.__doc__
        setattr(self, 'do_'+name, func)

class BaseCommand (object):
    
    """
    Basic command for the ``CommandLineInterpreter``. Subclass this if you want
    to add new commands. You MUST override ``handle()``!
    """

    #: usage string for option parser (--help option)
    usage = None

    def __init__(self, db):
        self.db = db

    def __call__(self, arg):
        parser = optparse.OptionParser(usage=self.usage, 
            description=self.__doc__.strip())
        # global options
        parser.add_option('-v', '--verbose', dest='verbose', action='count', 
            help='Be chatty about it!', default=0)
        # custom per-command options
        self.add_options(parser)

        option, args = parser.parse_args(arg.split())
        return self.handle(args, option)

    def add_options(self, parser):
        """
        Adds custom options to the command's option parser. This method can be
        overridden in subclasses - but does not have to be.
        """

    def handle(self, args, options):
        """
        Does the actual work. Absolutely, positively MUST be overridden in 
        subclasses!
        """
        raise NotImplementedError


class Collect (BaseCommand):

    """
    Collects download information for package.
    """

    usage = 'collect <package> URL [URL ...]'

    SOURCE_REG = {
        'bitbucket' : re.compile('(bit|byte)bucket\.org'),
        'pypi' : re.compile('pypi.python.org'),
        'github' : re.compile('github.com'),
    }

    def guess_source(self, url):
        "Get source identifier from URL."
        for key, reg in self.SOURCE_REG.items():
            if reg.search(url):
                return key
        return None

    def handle(self, parts, options):
        package = parts.pop(0)
        for url in parts:
            def subst(mobj):
                "Substitute shortcuts (like 'pypi:...')"
                return {
                    'pypi' : 'http://pypi.python.org/pypi/',
                    'bb' : 'http://bitbucket.org/',
                    'gh' : 'http://github.com/',
                }[mobj.group(1)]
            url = re.sub('(^\w+):(?!//)', subst, url)

            source = self.guess_source(url)

            try:
                print 'Fetching data from %s...' % url
                data = utils.get_downloads(url)
                self.db.add(package, data, source)
            except IOError, e:
                print "Error: Could not fetch source!"


class Dump (BaseCommand):

    """
    Exports data to CSV.
    """
    
    usage = 'dump [PACKAGE [VERSION]]'
    
    def add_options(self, parser):
        """
        Adds custom options to the command's option parser.
        """
        parser.add_option('-f', '--file', dest='file', 
            help='Write output to FILE.')
        parser.add_option('--nan', dest='nan', default='', 
            help='Symbol used for empty values (default: "%default")')
        parser.add_option('--total-values', dest='total', 
            action='store_true', default=False, 
            help='Show total download counts.')
        parser.add_option('--incremental-values', dest='total', 
            action='store_false', default=False, 
            help='Show incremetal download counts (default).')

    def handle(self, args, options):

        if options.file:
            print 'Writing to %s...' % options.file
            output = open(options.file, 'wb')
        else:
            output = sys.stdout
        
        # determine package and version
        while len(args) < 2:
            args += [None]
        pkg, ver = args
        
        try:
            output.write(self.db.tocsv(pkg, ver, 
                nan=options.nan, total=options.total))
            output.flush()
        except ValueError, e:
            print 'ERROR:', e


class ExportJSON (BaseCommand):
    
    """
    Exports data to simgle JSON file.
    """

    def handle(self, args, options):
        try:
            output = args[0]
            if output == '-':
                fp = sys.stdout
            else:
                fp = open(output, 'wb')
            print 'Exporting...'
            simplejson.dump([
                {version : {file : downloads}, '_package' : pkg, 
                '_source' : src, '_date' : date.strftime('%Y-%m-%d')} 
                for date, src, pkg, version, file, downloads in self.db
            ], fp)
        except IndexError:
            print 'ERROR: No output file specified!'


class ImportJSON (BaseCommand):
    
    """
    Imports data from JSON files.
    """

    def handle(self, args, options):
        paths = [os.path.expandvars(os.path.expanduser(path))
                 for path in args]
        if options.verbose > 0:
            print 'Paths:', paths
        files = (glob.glob(path) for path in paths)
        files = reduce(lambda a,b: a+b, files)
        print 'Found %i files.' % len(files)
        for filename in files:
            print 'Loading %s...' % filename
            try:
                blocks = storage.read_json(open(filename))
                if type(blocks) == dict:
                    blocks = [blocks]
                for data in blocks:
                    self.db.add(data['_package'], data, 
                        data['_source'], data['_date'])
            except ValueError, e:
                print 'ERROR:', e


def main(argv=sys.argv[1:]):
    """
    Main program.
    """
    # create config dir if not exists
    if not os.path.exists(CONFIG_DIR):
        os.mkdir(CONFIG_DIR)

#    # main config parser
#    parser = optparse.OptionParser()
#    parser.add_option('-q', '--quiet', dest='quiet', action='store_true',
#          help='Suppress output.', default=False)
#    opt, arg = parser.parse_args(argv)
#
#    if len(arg) == 0:
#        parser.print_help()
#        parser.exit()

    db = storage.DB(os.path.join(CONFIG_DIR, DATABASE))
    command = CommandLineInterpreter(db)
    command.register('collect', Collect)
    command.register('dump', Dump)
    command.register('import', ImportJSON)
    command.register('export', ExportJSON)
    
    if len(argv) > 0:
        command.onecmd(' '.join(argv))
    else:
        while not command.stop:
            try:
                command.cmdloop()
            except SystemExit:
                pass
    
if __name__ == '__main__':
    main()

    # single commands
    #main('collect python-amazon-product-api bb:basti/python-amazon-product-api'.split())    
    #main('collect python-weewar bb:basti/python-weewar -v'.split())    
    #main('dump -vvv'.split())
    #main('unknown'.split())
