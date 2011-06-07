from os.path import join, isdir, isfile, getmtime, exists, abspath
from os import walk, getcwd, chdir
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
    ( (?P<from>\w+) : (?P<to>\w+) )+
''', VERBOSE)

colors = dict (
    red = "\033[31;1m",
    lred = "\033[31;2m",
    green = "\033[32;1m",
    yellow = "\033[33;1m",
    normal = "\033[0m"
)

def _print_exc (exc):
    message = unicode (exc)
    if message:
        print ("  %(red)s%(ename)s%(normal)s : %(e)s" % dict (ename=exc.__class__.__name__, e=exc, **colors))
    else:
        print ("  %(red)s%(ename)s%(normal)s" % dict (ename=exc.__class__.__name__, e=exc, **colors))

def watch (options, parser, ctx):

    # Parsing the extension list.
    extensions = dict ()
    try:
        for ext in options.extensions.split (','):
            res = ext.split (':')
            extensions [ res[0] ] = res[1]
    except:
        parser.error ("File extensions were incorrectly specified.")

    dependancies = dict ()

    def default_output_filename (source):
        for k, v in extensions.items ():
            if source.endswith (k):
                return source[:-len(k)] + v
        return source + '.xml'

    def compile_file (source, dest):
        prev = options.output
        options.output = abspath (join (getcwd (), dest))
        src = abspath (join (getcwd (), source) )
        path = getcwd ()
        compilation_ok = False
        accessed = set ()
        try:
            compile_pwi (src, options, ctx, accessed)
            dependancies[source] = accessed
            compilation_ok = True
            if dest != "/dev/null":
                print ("  %(src)s %(green)s->%(normal)s %(dst)s" % dict (src=source, dst=dest, **colors))
        except Exception, e:
            print ("  %(src)s %(red)s!!%(normal)s %(red)s%(dst)s%(normal)s" % dict (src=source, dst=dest, **colors))
            _print_exc (e)
        finally:
            chdir (path)
        options.output = prev
        return compilation_ok

    _temporary_failure = dict ()
    def should_compile (source, dest):

        if not exists (dest) and (not source in _temporary_failure or getmtime (source) > _temporary_failure[ source ]):
            return True
        else:
            if not source in dependancies:
                compile_file (source, "/dev/null")

            _mtime = getmtime (dest) if not source in _temporary_failure else _temporary_failure[ source ]
            if getmtime (source) > _mtime:
                return True
            for dep in dependancies[source]:
                if getmtime (dep) > _mtime:
                    return True
        return False

    def create_file_watcher (source, dest):

        def _wrapper ():
            if should_compile (source, dest):
                if compile_file (source, dest):
                    # Compilation was successful, so we remove the source from the failure if it was there
                    if source in _temporary_failure:
                        del _temporary_failure[ source ]
                else:
                    _temporary_failure [dest] = getmtime (source)

        return _wrapper


    def create_directory_watcher (source, dest):

        def _wrapper ():
            to_compile = []
            for d, subdirs, files in walk (source, followlinks=True):
                for f in files:
                    _src = join (d, f)

                    for k, v in extensions.items ():
                        if f.endswith (k):
                            _dst = join (d.replace (source, dest), default_output_filename (f))

                            if should_compile (_src, _dst):
                                to_compile.append ( (_src, _dst ) )
                            break

            for _src, _dst in to_compile:
                if compile_file (_src, _dst):
                    if _src in _temporary_failure:
                        del _temporary_failure [ _src ]
                else:
                    _temporary_failure [ _src ] = getmtime ( _src )
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
            for w in watchers:
                w ()
            sleep (2)
        except KeyboardInterrupt, e:
            _print_exc (e)
            break

