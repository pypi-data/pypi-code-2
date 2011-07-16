"""backport module

A naive and probably incomplete script for backporting importlib to
Python 2.x.  The resulting importlib works under 2.4 and up, at least.

"""

import os
import shutil
import re


class Backport(object):
    """A simple class for transforming Python source files.

    """

    DEFAULT_PATH = "."
    PYTHON_EXTENSION = "py"
    BACKUP_EXTENSION = "orig"
    REPLACEMENTS = {}
    IGNORE = (__file__,)

    def __init__(self, path=DEFAULT_PATH, filenames=None, verbose=__debug__):
        if filenames is None:
            filenames = self.get_filenames(path)
        self.filenames = filenames
        self.verbose = verbose

    @classmethod
    def get_filenames(cls, path):
        filenames = os.listdir(path)
        for filename in filenames[:]:
            if filename in cls.IGNORE:
                filenames.remove(filename)
                continue
            try:
                name, ext = filename.rsplit(".", 1)
            except ValueError:
                filenames.remove(filename)
                continue
            if ext == cls.BACKUP_EXTENSION:
                if not name.endswith("."+cls.PYTHON_EXTENSION):
                    filenames.remove(filename)
                elif name.count(".") > 1:
                    filenames.remove(filename)
            elif "." in name:
                filenames.remove(filename)
            elif ext != cls.PYTHON_EXTENSION:
                filenames.remove(filename)
        return filenames
    
    def backup(self):
        for filename in self.filenames[:]:
            if not filename.endswith("."+self.PYTHON_EXTENSION):
                continue
            origfilename = filename + "." + self.BACKUP_EXTENSION
            if origfilename not in self.filenames:
                shutil.copy(filename, origfilename)
                self.filenames.append(origfilename)
    
    def restore(self, clean=False):
        for origfilename in self.filenames[:]:
            if not origfilename.endswith("."+self.BACKUP_EXTENSION):
                continue
            filename = origfilename.strip("."+self.BACKUP_EXTENSION)
            shutil.copy(origfilename, filename)
            if filename not in self.filenames:
                self.filenames.append(filename)
            if clean:
                os.remove(origfilename)
    
    def transform(self, source):
        for old, new in self.REPLACEMENTS.items():
            source = re.sub(old, new, source)
        return source

    def run(self, dryrun=True):
        self.backup()
        self.restore()
        
        for filename in self.filenames:
            if not filename.endswith(self.PYTHON_EXTENSION):
                continue

            infile = open(filename)
            source = infile.read()
            infile.close()
            
            source = self.transform(source)
            
            if self.verbose:
                print("")
                print(filename + "%%"*50)
                print(source)

            if not dryrun:
                open(filename, "w").write(source)


class ImportlibBackport(Backport):

    REPLACEMENTS = {
            # relative imports
            r"(?m)^from\s+\.\s+import\s": r"import ",
            r"(?m)^from\s+\.(\w+)\s+import\s": r"from \1 import ",

            # conditional expressions
            r"\((\S+)\s+if\s+(\S+)\s+else\s": r"(\2 and \1 or ",
            r"([^(\s]+)\s+if\s+(\S+)\s+else\s": r"\2 and \1 or ",

            # octal literals
            r"\s+&\s+0o": r" & 0",
            r",\s+0o": r", 0",

            # partition and rpartition
            r"\.partition": r".split",
            r"'rpartition'": r"'rsplit'",
            r"([\w.()]+).rpartition\((.+?)\)\[0\]":
                    r"\2 in \1 and \1.rsplit(\2, 1)[0] or ''",
            r"([\w.()]+).rpartition\((.+?)\)\[2\]":
                    r"\1.rsplit(\2, 1)[-1]",
            r"(\w+),\s*_,\s*(\w+)\s*=\s*(\w+)\.rpartition\((\w+)\)":
                    r"\1, \2 = \3.rsplit(\4, 1)",

            # keyword only arguments
            r",\s*\*\s*,": r",",

            # exception bindings
            r"\s+as\s+exc:": r", exc:",

            # function attributes
            r"\.__code__": r".func_code",

            # super
            r"super\(\)": r"super(_DefaultPathFinder, cls)",

            # new style classes
            r"class\s+(\w+):": r"class \1(object):",

            # with statements
            r"(\s*)with _io\.FileIO\(path, 'r'\) as file:\s*\n(.*?)\n":
                    r"\1file = open(path, 'rb')"
                    r"\1try:\n\2"
                    r"\1finally:\1    file.close()",
            r"(\s*)with _io\.FileIO\(path, 'wb'\) as file:\s*\n(.*?)\n":
                    r"\1file = open(path, 'wb')"
                    r"\1try:\n\2"
                    r"\1finally:\1    file.close()\n",
            r"(?s)(\s*)with _ImportLockContext\(\):\s*\n(.*?)\n\n":
                    r"\1imp.acquire_lock()"
                    r"\1try:\n\2"
                    r"\1finally:\1    imp.release_lock()\n\n",

            # kwargs for compile
            r"(?s),\s*'exec',\s*dont_inherit=True\)": r", 'exec', False, True)",

            # sys.dont_write_bytecode
            r"not sys.dont_write_bytecode": r"True",

            # imp.NullImporter
            r"(\s*)implicit_hooks\s*=\s*": 
                    r"\1class NullImporter(object):"
                    r"\1    def __init__(path_string):"
                    r"\1        if not path_string:"
                    r"\1            raise ImportError()"
                    r"\1        if path_string in sys.path_importer_cache:"
                    r"\1            raise ImportError()"
                    r"\1        return self"
                    r"\1    def find_module(fullname, path=None):"
                    r"\1        return None"
                    r"\1implicit_hooks = ",
            r"implicit_hooks\s*=\s*\[(.*)imp.NullImporter":
                    r"implicit_hooks = [\1NullImporter",
            
            # string.format
            r"\.format\((.*?)\)(\)?)([^)])": r" % (\1,)\2\3",
            r"([^=])\{\d?\}": r"\1%s",
            r"([^=])\{\d?!r\}": r"\1%r",

            # old-style relative imports
            r"(\s*)meta_path\s*=\s*sys.meta_path\s*[+]\s*_IMPLICIT_META_PATH":
                    r"\1else:"
                    r"\1    import inspect, os.path"
                    r"\1    path, _ = os.path.split(inspect.stack()[2][1])"
                    r"\1    path = [path] + sys.path"
                    r"\1meta_path = sys.meta_path + _IMPLICIT_META_PATH",

            # unavailable modules
            r", _io": r"",
            r"\._io\s+=\s+_io": r".imp = imp",
            r"(?sm)^(\s*)encoding = .*?encoding\[0\]\)\)": 
                    r"\1return source_bytes",
            r"import _warnings": r"import warnings as _warnings",

            # PEP 3147
            r"imp.cache_from_source\((.*)\)": r"\1+'c'",

            # unavailable methods
            r"(\s*)imp\._fix_co_filename\(found, source_path\)":
                    r"\1if found.co_filename != source_path:"
                    r"\1    raise NotImplementedError()"
                    r"\1    imp._fix_co_filename(found, source_path)",

            # bytes
            r"bytearray": r"str",
            r"data\.extend": r"data += ",
            r"([^(])(int_bytes\[\d\])": r"\1ord(\2)",
            }

    def test(self):
        from  __init__ import __import__
        __builtins__.__import__ = __import__

        # test a stdlib import
        import logging

        # set up the test
        import tempfile
        temppath = tempfile.mkdtemp()
        import sys
        sys.path.append(temppath)
        import os.path
        pkgpath = os.path.join(temppath, "backport_test")
        os.mkdir(pkgpath)
        open(os.path.join(pkgpath, "__init__.py"), "w").write(
                "import relative")
        open(os.path.join(pkgpath, "relative.py"), "w").write(
                "PI = 3.14159265")

        # test a custom package with local relative import
        import backport_test
        print(backport_test.relative.PI)

        # clean up
        import shutil
        shutil.rmtree(temppath)


if __name__ == "__main__":
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-q", "--quiet",
                      action="store_true", default=False,
                      help="Don't write the transformed source to stdout.")
    parser.add_option("--path",
                      help="The path to the directory to backport.")
    parser.add_option("--dry",
                      action="store_true", default=False,
                      help="Don't write the transformed source")
    parser.add_option("--test",
                      action="store_true", default=False,
                      help="Test the current package")
    parser.add_option("--clean",
                      action="store_true", default=False,
                      help="Restore the path to their original state.")
    (options, args) = parser.parse_args()

    path = options.path or Backport.DEFAULT_PATH
    backport = ImportlibBackport(path, verbose=not options.quiet)

    if options.clean:
        backport.restore(True)
    elif options.test:
        backport.test()
    else:
        backport.run(options.dry)
        backport.test()



