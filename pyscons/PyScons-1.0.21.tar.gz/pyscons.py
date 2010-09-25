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

This does three things:

1. Installs a builder: PyScript.
2. Installs a builder: PyScons.
3. Installs a new scanner for python scripts.

PyScript
--------

This Builder runs python scripts and modules. 

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

PyScons (experimental)
----------------------

This Builder enables running a python script as if it is a scons script. 

This is distinct from SConscript which functions like an include. Instead, PyScons spawns a new scons process.
Spawning a new process allows for temporary files to be automatically deleted without triggering a rebuild.

To use this builder, create a .py file with, for example, the following code in a file (my_scons.py)::

    from pyscons import PySconsSetup
    targets, sources, basename = PySconsSetup()
   
    temp = basename + ".temp"

    PyScript(temp, ["step1.py"] + sources, capture="out")
    Pyscript(targets, ["step2.py", temp], capture="out")
 
Now, this file can be called from a SConstruct file like so::

    PyScons(targets, sources, "my_scons.py", options = "-j4")

The temp file be generated if it is required to generate targets, but will be immediately deleted.
This is useful for builders which generate large intermediate files which would should be deleted
without triggering a rebuild. This can be better than passing a list to the Command function for a 
few special cases:

1. PyScons enables parallel execution of a multistep submodule(if you pass the -j option to the spawned scons) 
2. PyScons creates a workflow environment (like Pipeline Pilot) in scons which enables complex tasks to be packaged in scons files for use in other scons files.
3. PyScons can turn intermediate file deletion on and off with a single flag::

    PyScons(targets, sources, "my_scons.py", clean = True) # intermediate file deleted
    PyScons(targets, sources, "my_scons.py", clean = False) # intermediate file retained

Unfortunately, dependency tracking does not propagate up from the spawned scons. So 
sources that are not explicitely included in the "sources" variable will not be tracked. There 
may be no good way around this, short of creating a new scanner and file extension (which I 
may do if there interest in this feature).

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
from SCons.Script import ARGUMENTS, DefaultEnvironment

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
        imports = [m.__file__ for m in self.modules.values() if m.__file__ != None]
        imports = list(os.path.abspath(m) for m in imports if self.path_filter(m))
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

def _PyScons(env, target, source, scons, options="-Q", clean = True):
    target = ToList(target) 
    source = ToList(source) 

    args = " ".join(["in%g=%s" % (n+1, str(s)) for n,s in enumerate(source)])
    args += " " + " ".join(["out%g=%s" % (n+1, str(s)) for n,s in enumerate(target)])

    if env.GetOption("clean") and not clean: env.Execute("scons %s -f%s %s --clean" % (options, scons, args))

    cmd = "scons %s -f${SOURCES[-1]} %s" % (options, args)
    if clean: cmd = [cmd, "scons %s -f${SOURCES[-1]} %s --clean" % (options, args)]

    return env.Command(target, source + [scons], cmd)

PyScons = DefaultEnvironmentCall("PyScons")
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
        env.AddMethod(_PyScons, "PyScons")
        return env

def PySconsSetup(args=ARGUMENTS, tools=['default', PYTOOL()]):
    env = DefaultEnvironment(ENV=os.environ, tools=tools)

    sources = []
    targets = []
    for a in args:
        if a[:2] == "in":
            try:
                i = int(a[2:])
                sources.append((i, args[a]))
            except: pass
        if a[:3] == "out":
            try:
                i = int(a[3:])
                targets.append((i, args[a]))
            except: pass
    sources = [a for i,a in sorted(sources)]
    targets = [a for i,a in sorted(targets)]

    env.NoClean(targets)
    
    try: basename = args["base"] 
    except: basename = None

    if basename == None: 
        try: basename = targets[-1]
        except: basename = "TEMP"

    return targets, sources, basename

