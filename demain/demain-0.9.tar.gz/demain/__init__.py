# -*- coding: utf-8 -*-
u"""Routine that fixes Python's broken __name__ == '__main__' behavior.

This package provides a clean solution for the case where you want to
write a Python module that can safely be invoked from the command line
but which also needs to be imported by other modules.  Simply write each
module that would normally make a ``__name__`` ``==`` ``'__main__'``
check like this instead::

    'Your module docstring'

    import demain
    __main__ = demain.fix()

    # Your other import statements
    # Your classes and functions

    if __main__:
        # Your code that gets invoked from the command line

In cases where your module has simply been imported by another module,
the ``fix()`` function does nothing and returns ``False``.  But if your
module has been invoked directly, either as a script or using Python's
``-m`` option, then ``fix()`` will:

* Replace your module's ``__name__`` global variable with its true name.
* Re-register your module in ``sys.modules`` under its true name, so that
  later ``import`` statements by other Python modules can find it.
* If your module is beneath a package, then the module is inserted into
  the package under its correct name.
* After making these corrections, the function returns ``True`` so that
  your module can detect that it is running as the main program.

I advocate that a future version of Python stop mangling module names
altogether, and instead set a ``__main__`` boolean in every module like
`demain` does.  But until then, use ``demain`` to bring your programs
some sanity, safely, and fewer mysterious breakages and error messages.

Background
----------

When you run a Python script from the command line, or invoke a module
using the ``-m`` option, Python gives that script or module the fake
name ``'__main__'`` so that it can detect that it is running as the
“main program.”  Consider a small script that looks like this::

    # foo.py
    print __name__

Invoking it from the command line obliterates the normal ``foo`` name
which it would have otherwise (as we can demonstrate, by importing the
module from the command line)::

    $ python foo.py
    __main__
    $ python -m foo
    __main__
    $ python -c 'import foo'
    foo

This name mangling causes no end of trouble when used with modules that
themselves are targets of importation, because the first attempt to
import the module under its real name results in a duplicate of the
module being created, with its own copy of every object and class.  The
bugs that this causes tend to be particularly difficult to track down.

The ``demain.fix()`` function is designed to prevent this problem from
even starting, by being the very first thing that you call at the top of
every module that you intend to be invoked directly.  Be careful not
only to avoid doing other imports before before running ``fix()`` but
also make sure that you create no classes first; otherwise, the name
``'__main__'`` will get copied into your classes as their module's name.

I knew that I finally had to do something about this problem when I read
*Defending Pyramid's Design* and reached Chris McDonough's anguished
plea in the section titled, “Application Programmers Don’t Control The
Module-Scope Codepath.”

http://docs.pylonshq.com/pyramid/dev/designdefense.html

There, his long experience with Python and his sharply-honed coding
practices lead him to make some excellent recommendations against the
dangers that small Python applications — and in particular those written
using Web micro-frameworks — incur when they treat a script as though it
were a normal module.  My hope is that ``demain`` will solve this
problem by making an invoked Python script a safe place for objects,
instead of having them all duplicated when the same Python file is
imported from elsewhere in the application using a normal import.

This package comes with a modest test suite, built from a few hand-built
examples, as well as McDonough's sample decorator framework that shows
the problem with Python's handling of script invocation.  To run it,
simply type::

    $ python -m demain.tests

"""
import inspect, os, sys

def compute_name(module):
    """Determine what `module` should have been named."""
    name = os.path.basename(module.__file__).split('.')[0]
    if module.__package__:  # None for scripts, '' for -m top_level_module
        fullname = module.__package__ + '.' + name
        return fullname, name
    return name, name

def fix_main():
    """Give the module named ``__main__`` its real name instead."""
    module = sys.modules['__main__']
    fullname, name = compute_name(module)
    module.__name__ = fullname
    sys.modules[fullname] = module
    if module.__package__:
        setattr(sys.modules[module.__package__], name, module)

def fix():
    """Fix the caller's module and return `True` if it is ``__main__``."""
    caller_globals = inspect.stack()[1][0].f_globals
    if caller_globals['__name__'] == '__main__':
        fix_main()
        return True
    return False
