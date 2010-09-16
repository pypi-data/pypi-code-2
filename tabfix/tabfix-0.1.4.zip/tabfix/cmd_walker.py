# (c) 2010 Martin Wendt; see http://tabfix.googlecode.com/
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
"""
Helpers to implement a recursive file processing command line script.
"""
from optparse import OptionParser
import os
import shutil
from fnmatch import fnmatch
import string
import time

TEMP_SUFFIX = ".$temp"
BACKUP_SUFFIX = ".bak"

#===============================================================================

_text_characters = "".join(map(chr, range(32, 127)) + list("\n\r\t\b"))
_null_trans = string.maketrans("", "")

def isTextFile(filename, blocksize=512):
    # Author: Andrew Dalke
    # http://code.activestate.com/recipes/173220-test-if-a-file-or-string-is-text-or-binary/
    try:
        s = open(filename).read(blocksize)
    except IOError:
        return False

    if "\0" in s:
        return False
    if not s:  # Empty files are considered text
        return True

    # Get the non-text characters (maps a character to itself then
    # use the 'remove' option to get rid of the text characters.)
    t = s.translate(_null_trans, _text_characters)

    # If more than 30% non-text characters, then
    # this is considered a binary file
    if float(len(t))/len(s) > 0.30:
        return False
    return True

#===============================================================================

def incrementData(data, key, inc=1):
    if type(data) is dict:
        if key in data:
            data[key] += inc
        else:
            data[key] = inc
    return


#===============================================================================
# WalkerOptions
#===============================================================================
class WalkerOptions(object):
    """Common options used by cmd_walker.process().
    
    This class 
    An implementation should derive its options from this base class and call
    cmd_walker.addCommonOptions().
    . cutomized This object, may be used instead of command line args.
    """
    def __init__(self):
#        self.match = None
        self.matchList = None
        self.targetPath = None
        self.backup = True
        self.dryRun = False
        self.recursive = False
        self.verbose = 1


#===============================================================================
# Walker 
#===============================================================================
def _processFile(fspec, opts, func, data):
    assert os.path.isfile(fspec)
    fspec = os.path.abspath(fspec)

    try:
        targetFspec = opts.targetPath or fspec
        targetFspec = os.path.abspath(targetFspec)

        assert not fspec.endswith(TEMP_SUFFIX)
        assert not targetFspec.endswith(TEMP_SUFFIX)
        tempFspec = fspec + TEMP_SUFFIX
        if os.path.exists(tempFspec):
            os.remove(tempFspec)

        try:
            data["files_processed"] += 1
            res = func(fspec, tempFspec, opts, data)
            if res is not False:
                data["files_modified"] += 1
        except Exception:
            data["exceptions"] += 1
            raise
        # 
        if res is False or opts.dryRun:
            # If processor returns False (or we are in dry run mode), don't 
            # change the file
            if os.path.exists(tempFspec):
                os.remove(tempFspec)
        elif opts.backup:
            bakFilePath = "%s%s" % (targetFspec, BACKUP_SUFFIX)
            if os.path.exists(bakFilePath):
                os.remove(bakFilePath)
            if os.path.exists(targetFspec):
                shutil.move(targetFspec, bakFilePath)
            shutil.move(tempFspec, targetFspec)
        else:
            if os.path.exists(targetFspec):
                os.remove(targetFspec)
            shutil.move(tempFspec, targetFspec)
    except Exception:
        raise
    return


def _processPattern(path, opts, func, data):
    assert opts.matchList
    assert os.path.isdir(path)
    assert not opts.targetPath
    for f in os.listdir(path):
        match = False
        for m in opts.matchList: 
            if m and fnmatch(f, m):
                match = True
                break
        if match:
            f = os.path.join(path, f)
            if os.path.isfile(f):
                _processFile(f, opts, func, data)
    return


def _processRecursive(path, opts, func, data):
    # Handle recursion or file patterns
    assert opts.recursive
    assert opts.matchList
    assert os.path.isdir(path)
    data["dirs_processed"] += 1
    _processPattern(path, opts, func, data)
    for root, dirnames, _filenames in os.walk(path):
        for dir in dirnames:
            data["dirs_processed"] += 1
            _processPattern(os.path.join(root, dir), opts, func, data)
    return


def process(args, opts, func, data):
    data.setdefault("elapsed", 0)
    data.setdefault("elapsed_str", "n.a.")
    data.setdefault("files_processed", 0)
    data.setdefault("files_modified", 0)
    data.setdefault("exceptions", 0)
    data.setdefault("dirs_processed", 0)
    start = time.clock()

    if opts.recursive:
        assert len(args) == 1
        _processRecursive(args[0], opts, func, data)
    elif opts.matchList:
        assert len(args) == 1
        _processPattern(args[0], opts, func, data)
    else:
        for f in args:
            _processFile(f, opts, func, data)

    data["elapsed"] = time.clock() - start
    data["elapsed_string"] = "%.3f sec" % data["elapsed"]
    
#    if opts.dryRun and opts.verbose >= 1:
#        print("\n*** Dry-run mode: no files have been modified!\n"
#              " ***Use -x or --execute to process files.\n")
    return




def addCommonOptions(parser):
    """Return a valid options object.
    @param parser: OptionParser
    """
#    parser.add_option("-d", "--dry-run",
#                      action="store_true", dest="dryRun", default=False,
#                      help="dry run: just print converted lines to screen")
    parser.add_option("-x", "--execute",
                      action="store_false", dest="dryRun", default=True,
                      help="turn off the dry-run mode (which is ON by default), " 
                      "that would just print status messages but does not change "
                      "anything")
    parser.add_option("-m", "--match",
                      action="append", dest="matchList",
                      help="match this file name pattern (option may be repeated)")
    parser.add_option("-o", "--target",
                      action="store", dest="targetPath", default=None,
                      metavar="FILENAME",
                      help="name of output file")
    parser.add_option("", "--no-backup",
                      action="store_false", dest="backup", default=True,
                      help="prevent creation of backup files (*.bak)")
    parser.add_option("-r", "--recursive",
                      action="store_true", dest="recursive", default=False,
                      help="visit sub directories")
    parser.add_option("-q", "--quiet",
                      action="store_const", const=0, dest="verbose", 
                      help="don't print status messages to stdout (verbosity 0)")
#    parser.add_option("-q", "--quiet",
#                      action="store_true", const=0, dest="quiet", default=False,
#                      help="don't print status messages (verbose 0)")
#    def quietCallback(option, opt_str, value, parser, *args, **kwargs):
#        pass
#    parser.add_option("-q", "--quiet",
#                      action="callback", callback=quietCallback,
#                      help="don't print status messages (verbosity 0).")
    parser.add_option("-v", "--verbose",
                      action="count", dest="verbose", default=1,
                      help="increment verbosity to 2 (use -vv for 3, ...)")
#    parser.add_option("--debug",
#                      action="store_const", const=3, dest="verbose", default=1,
#                      help="don't print status messages (verbose 3)")
    return




def checkCommonOptions(parser, options, args):
    """Validate common options."""
#    if len(args) != 1:
#        parser.error("expected exactly one source file or folder")
    # TODO:
#    if options.quiet and options.verbose:
#        parser.error("options -q and -v are mutually exclusive")
    if options.matchList and not args:
        args.append(".")

    if len(args) < 1:
        parser.error("missing required PATH")
    elif options.targetPath and len(args) != 1:
        parser.error("-o option requires exactly one source file")
    elif options.recursive and len(args) != 1:
        parser.error("-r option requires exactly one source directory")
    elif options.recursive and not options.matchList:
        parser.error("-r option requires -m")

    for f in args:
        if not os.path.exists(f):
            parser.error("input not found: %r" % f)
        elif os.path.isdir(f) and not options.matchList:
            parser.error("must specify a match pattern, if source is a folder")
        elif os.path.isfile(f) and options.matchList:
            parser.error("must not specify a match pattern, if source is a file")
#    if not os.path.exists(args[0]):
#        parser.error("input not found: %r" % args[0])
#    elif os.path.isdir(args[0]) and not options.match:
#        parser.error("must specify a match pattern, if source is a folder")
#    elif os.path.isfile(args[0]) and options.match:
#        parser.error("must not specify a match pattern, if source is a file")
    
    if options.targetPath and options.matchList:
        parser.error("-m and -o are mutually exclusive")
    return True




#===============================================================================
# Sample processor
#===============================================================================
def piggify(fspec, targetFspec, opts, data):
    """Sample file processor."""
    pass




def test():
    # Create option parser for common and custom options
    parser = OptionParser(usage="usage: %prog [options] PATH",
                          version="0.0.1")

    parser.add_option("-c", "--count",
                      action="store", dest="count", default=3,
                      metavar="COUNT",
                      help="number of '.' to prepend (default: %default)")

    addCommonOptions(parser)
    
    # Parse command line
    (options, args) = parser.parse_args()

    # Check syntax  
    checkCommonOptions(parser, options, args)

    try:
        count = int(options.count)
    except:
        count = 0
    if count < 1:
        parser.error("count must be numeric and greater than 1")
    
    # Call processor
    data = {}
    process(args, options, piggify, data)
    


if __name__ == "__main__":
    test()
