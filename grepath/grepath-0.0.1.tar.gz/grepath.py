#!/usr/bin/env python
"""Find executables in %PATH% that match PATTERN.

"""
#XXX: remove --use-pathext option

import fnmatch, itertools, os, re, sys, warnings
from optparse  import OptionParser
from stat import S_IMODE, S_ISREG, ST_MODE
from subprocess import PIPE, Popen


def warn_import(*args):
    """pass '-Wd' option to python interpreter to see these warnings."""
    warnings.warn("%r" % (args,), ImportWarning, stacklevel=2)


class samefile_win:
    """
    http://timgolden.me.uk/python/win32_how_do_i/see_if_two_files_are_the_same_file.html
    """
    @staticmethod
    def get_read_handle (filename):
        return win32file.CreateFile (
            filename,
            win32file.GENERIC_READ,
            win32file.FILE_SHARE_READ,
            None,
            win32file.OPEN_EXISTING,
            0,
            None
            )

    @staticmethod
    def get_unique_id (hFile):
        (attributes,
         created_at, accessed_at, written_at,
         volume,
         file_hi, file_lo,
         n_links,
         index_hi, index_lo
         ) = win32file.GetFileInformationByHandle (hFile)
        return volume, index_hi, index_lo

    @staticmethod
    def samefile_win(filename1, filename2):
        """Whether filename1 and filename2 represent the same file.

        It works for subst, ntfs hardlinks, junction points.
        It works unreliably for network drives.

        Based on GetFileInformationByHandle() Win32 API call.
        http://timgolden.me.uk/python/win32_how_do_i/see_if_two_files_are_the_same_file.html
        """
        if samefile_generic(filename1, filename2): return True
        try:
            hFile1 = samefile_win.get_read_handle (filename1)
            hFile2 = samefile_win.get_read_handle (filename2)
            are_equal = (samefile_win.get_unique_id (hFile1)
                         == samefile_win.get_unique_id (hFile2))
            hFile2.Close ()
            hFile1.Close ()
            return are_equal
        except win32file.error:
            return None


def canonical_path(path):
    """NOTE: it might return wrong path for paths with symbolic links."""
    return os.path.realpath(os.path.normcase(path))


def samefile_generic(path1, path2):
    return canonical_path(path1) == canonical_path(path2)


class is_executable_destructive:
    @staticmethod
    def error_message(barename):
        r"""
        "'%(barename)s' is not recognized as an internal or external\r\n
        command, operable program or batch file.\r\n"

        in Russian:
        """
        return '"%(barename)s" \xad\xa5 \xef\xa2\xab\xef\xa5\xe2\xe1\xef \xa2\xad\xe3\xe2\xe0\xa5\xad\xad\xa5\xa9 \xa8\xab\xa8 \xa2\xad\xa5\xe8\xad\xa5\xa9\r\n\xaa\xae\xac\xa0\xad\xa4\xae\xa9, \xa8\xe1\xaf\xae\xab\xad\xef\xa5\xac\xae\xa9 \xaf\xe0\xae\xa3\xe0\xa0\xac\xac\xae\xa9 \xa8\xab\xa8 \xaf\xa0\xaa\xa5\xe2\xad\xeb\xac \xe4\xa0\xa9\xab\xae\xac.\r\n' % dict(barename=barename)

    @staticmethod
    def is_executable_win_destructive(path):
        # assume path <-> barename that is false in general
        barename = os.path.splitext(os.path.basename(path))[0]
        p = Popen(barename, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = p.communicate()
        return p.poll() != 1 or stdout != '' or stderr != error_message(barename)


def is_executable_win(path):
    """Based on:
    http://timgolden.me.uk/python/win32_how_do_i/tell-if-a-file-is-executable.html

    Known bugs: treat some "*~" files as executable, e.g. some "*.bat~" files
    """
    try:
        _, executable = FindExecutable(path)
        return bool(samefile(GetLongPathName(executable), path))
    except error:
        return None # not an exe or a document with assoc.


def is_executable_posix(path):
    """Whether the file is executable.

    Based on which.py from stdlib
    """
    #XXX it ignores effective uid, guid?
    try: st = os.stat(path)
    except os.error:
        return None

    isregfile = S_ISREG(st[ST_MODE])
    isexemode = (S_IMODE(st[ST_MODE]) & 0111)
    return bool(isregfile and isexemode)

try:
    #XXX replace with ctypes?
    from win32api import FindExecutable, GetLongPathName, error
    is_executable = is_executable_win
except ImportError, e:
    warn_import("is_executable: fall back on posix variant", e)
    is_executable = is_executable_posix

try: samefile = os.path.samefile
except AttributeError, e:
    warn_import("samefile: fallback to samefile_win", e)
    try:
        import win32file
        samefile = samefile_win.samefile_win
    except ImportError, e:
        warn_import("samefile: fallback to generic", e)
        samefile = samefile_generic

def main():
    parser = OptionParser(usage="""
  %prog [options] PATTERN
  %prog [options] -e PATTERN""", description=__doc__)
    opt = parser.add_option
    opt("-e", "--regex", metavar="PATTERN",
        help="use PATTERN as a regular expression")
    opt("--ignore-case", action="store_true", default=True,
        help="""[default] ignore case when --regex is present; for \
 non-regex PATTERN both FILENAME and PATTERN are first \
 case-normalized if the operating system requires it otherwise \
 unchanged.""")
    opt("--no-ignore-case", dest="ignore_case", action="store_false")
    opt("--use-pathext", action="store_true", default=True,
        help="[default] whether to use %PATHEXT% environment variable")
    opt("--no-use-pathext", dest="use_pathext", action="store_false")
    opt("--show-non-executable", action="store_true", default=False,
        help="show non executable files")

    (options, args) = parser.parse_args()

    if len(args) != 1 and not options.regex:
       parser.error("incorrect number of arguments")
    if not options.regex:
       pattern = args[0]
    del args

    if options.regex:
       filepred = re.compile(options.regex, options.ignore_case and re.I).search
    else:
       fnmatch_ = fnmatch.fnmatch if options.ignore_case else fnmatch.fnmatchcase
       for file_pattern_symbol in "*?":
           if file_pattern_symbol in pattern:
               break
       else: # match in any place if no explicit file pattern symbols supplied
           pattern = "*" + pattern + "*"
       filepred = lambda fn: fnmatch_(fn, pattern)

    if not options.regex and options.ignore_case:
       filter_files = lambda files: fnmatch.filter(files, pattern)
    else:
       filter_files = lambda files: itertools.ifilter(filepred, files)

    if options.use_pathext:
       pathexts = frozenset(map(str.upper,
            os.environ.get('PATHEXT', '').split(os.pathsep)))

    seen = set()
    for dirpath in os.environ.get('PATH', '').split(os.pathsep):
        if os.path.isdir(dirpath): # assume no expansion needed
           # visit "each" directory only once
           # it is unaware of subst drives, junction points, symlinks, etc
           rp = canonical_path(dirpath)
           if rp in seen: continue
           seen.add(rp); del rp

           for filename in filter_files(os.listdir(dirpath)):
               path  = os.path.join(dirpath, filename)
               isexe = is_executable(path)

               if isexe == False and is_executable == is_executable_win:
                  # path is a document with associated program
                  # check whether it is a script (.pl, .rb, .py, etc)
                  if not isexe and options.use_pathext:
                     ext   = os.path.splitext(path)[1]
                     isexe = ext.upper() in pathexts

               if isexe:
                  print path
               elif options.show_non_executable:
                  print "non-executable:", path


if __name__=="__main__":
   main()
