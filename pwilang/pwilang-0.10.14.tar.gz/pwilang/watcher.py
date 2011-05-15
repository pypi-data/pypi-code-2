from os.path import join, isdir, isfile, getmtime, exists
from os import walk
from time import sleep
from pwilang import compile_pwi
from traceback import print_exc
import sys

from re import compile, VERBOSE

re_watch_expression = compile ('''
                          (,?            # There can be a leading comma
                            (?P<src>[^:]+) # Source filename
                                (:                 # Separated by ':'
                                (?P<dst>[^,]*) )?      # Optional Destination
                          )+
                          ''',
                          VERBOSE)

re_extensions = compile ('''
    ( ,? (?P<from>\w+) : (?P<to>\w+) )+
''', VERBOSE)

colors = dict (
    red = "\033[31;1m",
    lred = "\033[31;2m",
    green = "\033[32;1m",
    yellow = "\033[33;1m",
    normal = "\033[0m"
)

def watch (options, parser, ctx):

    # Parsing the extension list.
    extensions = dict ()
    for match in re_extensions.finditer (options.extensions):
        extensions [ match.group ("from") ] = match.group ("to")
    if not extensions:
        parser.error ("File extensions were incorrectly specified.")

    def default_output_filename (source):
        for k, v in extensions.items ():
            if source.endswith (k):
                return source[:-len(k)] + v
        return source + '.xml'

    def compile_file (source, dest):
        prev = options.output
        options.output = dest
        try:
            compile_pwi (source, options, ctx)
            print ("  %(src)s %(green)s->%(normal)s %(dst)s" % dict (src=source, dst=dest, **colors))
        except Exception, e:
            print ("  %(src)s %(red)s!!%(normal)s %(dst)s%(lred)s" % dict (src=source, dst=dest, **colors))
            print_exc (e)
            print colors["normal"],

        options.output = prev

    def create_file_watcher (source, dest):

        def _wrapper ():
            if not exists (dest) or getmtime (source) > getmtime (dest):
                compile_file (source, dest)

        return _wrapper


    def create_directory_watcher (source, dest):

        def _wrapper ():
            for d, subdirs, files in walk (source, followlinks=True):
                for f in files:
                    _src = join (d, f)
                    for k, v in extensions.items ():
                        if f.endswith (k):
                            _dst = join (d.replace (source, dest), default_output_filename (f))

                            if not exists (_dst) or getmtime (_src) > getmtime (_dst):
                                compile_file (_src, _dst)
                        break
        return _wrapper

    watchers = []

    for match in re_watch_expression.finditer (options.watch):
        src = match.group ('src')
        dst = match.group ('dst')

        if isfile (src):
            if not dst: dst = default_output_filename (src)
            watchers.append (create_file_watcher (src, dst))
            print ("  %(green)s*%(normal)s Watching file %(yellow)s%(src)s%(normal)s -> %(yellow)s%(dst)s%(normal)s" % dict (src=src, dst=dst, **colors) )

        elif isdir (src):
            if not dst: dst = src
            watchers.append (create_directory_watcher (src, dst))
            print "  %(green)s*%(normal)s Watching files in directory %(yellow)s%(src)s%(normal)s -> %(yellow)s%(dst)s%(normal)s" % dict (src=src, dst=dst, **colors)

        else:
            parser.error ("All specified files and directory to be watched MUST exist")

    if not watchers:
        parser.error ("Items to be watched were incorrectly specified")

    while True:
        try:
            sleep (2)
            for w in watchers:
                w ()
        except Exception, e:
            print ("  %(red)s!!%(normal)s Stopping Watcher" % colors)
            raise e
