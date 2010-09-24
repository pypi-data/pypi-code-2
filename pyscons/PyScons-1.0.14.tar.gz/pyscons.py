"""
=======
PyScons
=======

PyScons is a tool which works with Scons_. It 
is installed into a new environment with either of the two commands::

    from pyscons import PYTOOL
    env = Environment(tools = ['default', PYTOOL()])

or::

    from pyscons import PYTOOL
    env = Environment()
    PYTOOL()(env)

This does two things:

1. Installs a new builder: PyScript.
2. Installs a new scanner for python scripts.

PyScript
--------

This Builder has a few additional abilities. 

First, it will automatically find the ".py" files referred to when 
running a module as a script with the '-m' option. For example
the following code will run a module as script and add the appriate files
to the dependencies::

   env.PyScript("out", ["-m timeit", "myscript.py"], "python $SOURCES > $TARGET")

Second, it defaults the command string to "python $SOURCES" and using the "capture"
keyword argument, can automatically append the appropriate strings to capture
the output or error (or both) to the targets::

   env.PyScript("out", ["-m timeit", "myscript.py"], capture="output")
   
or to capture both the output and error::
  
   env.PyScript(["out","err"], ["-m timeit", "myscript.py"], capture="both")
   
Just like Command, multiple steps can be used to create a file::

   env.PyScript("out", ["step1.py", "step2.py"], 
        ["python ${SOURCES[0]} > temp", "python ${SOURCES[1]} > $TARGET", Delete("temp")])

PyScanner
---------

This scanner uses the modulefinder module to find all import dependencies 
in all sources with a 'py' extension. It can take two options in its constructor:

1. filter_path: a callable object (or None) which takes a path as input and returns true
   if this file should be included as a dependency by scons, or false if it should be ignored.
   By default, this variable becomes a function which ensures that no system python modules
   or modules from site-packages are tracked. To track all files, use "lambda p: True".

2. recursive: with a true (default) or false, it enables or disables recursive dependency 
   tracking. 

For example to track all files (including system imports) in a nonrecursive scanner, use
the following install code in your SConstruct::

    from pyscons import PYTOOL
    env = Environment(tools = ['default', PYTOOL(recursive = False, filter_path = lambda p: True)])

Known Issues
------------

Relative imports do not work. This seems to be a bug in the modulefinder package that I do not 
know how to fix.

Author
------

S. Joshua Swamidass (homepage_)

.. _homepage: http://swami.wustl.edu/
.. _Scons: http://www.scons.org/
"""

import os
from SCons import Util
from SCons.Scanner import Scanner
from SCons.Script.SConscript import DefaultEnvironmentCall
from modulefinder import ModuleFinder as MF

class PyScanner(MF):
    """
    A scanner for py files which finds all the import dependencies.
    """
    def __init__(self, path_filter, *args, **kwargs):
        self.path_filter = path_filter
        MF.__init__(self, *args, **kwargs)

    def import_hook(self, name, caller, *arg, **karg):
        if caller.__file__ == self.name: 
            return MF.import_hook(self, name, caller, *arg, **karg) 

    def __call__(self, node, env, path):
        if str(node).split('.')[-1] not in ['py', 'pyc', 'pyo']: return []
        self.modules = {}; self.name = str(node)
        try: self.run_script(self.name)
        except: pass
        imports = list(os.path.abspath(m.__file__) for m in self.modules.values() 
            if self.path_filter(m.__file__))
        return imports

def ToList(input):
    if input is None: input = [] 
    elif not Util.is_List(input): input = [input]
    return input

def _PyScript(env, target, source, command = "python $SOURCES", 
                    capture=None, *args, **kwargs): 
    """
    A new Builder added to a scons environment which has the same syntax as Command.
    """
    target = ToList(target)
    source = ToList(source) 
    subst = list(source)
    command = ToList(command)

    for n,s in enumerate(source): 
        s = str(s)
        if s.strip()[:3] == "-m ":
            module = s.strip()[3:]
            s = os.popen("python -c 'import %s as M; print M.__file__'" 
                                    % module).read().strip()
        if s[-3:] in ["pyc", "pyo"]: s = s[:-1]
        source[n] = s
    
    if capture in ["stdout", "out", "output"]: command[-1] += " > $TARGET"
    elif capture in ["stderr", "err", "error"]: command[-1] += " 2> $TARGET"
    elif capture == "join": command[-1] += " &> $TARGET"
    elif capture == "both": command[-1] += " > ${TARGETS[0]} 2> ${TARGETS[1]}"
    elif capture == None: pass
   
    command = [ env.subst(c, target=target, source=subst) for c in command ]
    return env.Command(target, source, command, *args, **kwargs)  

PyScript = DefaultEnvironmentCall("PyScript")

class PYTOOL:
    def __init__(self, path_filter = None, recursive=True):
        if path_filter == None: 
            pythonos = os.__file__.strip("os.pyc").strip("os.py")
            path_filter = lambda p: pythonos not in p
        self.path_filter = path_filter
        self.recursive = recursive

    def __call__(self, env):
        env.Append(SCANNERS = Scanner(function = PyScanner(self.path_filter), 
                    name = "PyScanner", skeys = ['.py', '.pyo', '.pyc'], recursive=self.recursive))
        env.AddMethod(_PyScript, "PyScript")
        return env
