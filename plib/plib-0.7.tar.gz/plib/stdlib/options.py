#!/usr/bin/env python
"""
Module OPTIONS -- Option Parser Utilities
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2011 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains a utility function for option parsers, to
reduce the amount of work needed to make use of the optparse
library module. Instead of having to manually instantiate an
option parser, add options to it, then call its parsing method,
the parse_options function wraps it all into one package; you
give it a list of option parameters and arguments and it
returns the parsed (options, args) tuple. This also allows
adding extra functionality:

- Argument checking: a list of argument names can be passed
  to the ``parse_options`` function, to allow display of
  expected arguments in the help, and to check that the correct
  number of arguments are present in the command line;

- Option dictionary: the options object (the first element of
  the 2-tuple returned by ``parse_options``) supports an
  immutable mapping interface, using the destination variable
  names passed in the option list as keys. This makes it
  easier to use the options to update other data structures
  in the program (see the gui-display.py example program for
  an illustration of this usage).
"""

import optparse
from itertools import imap, izip

from plib.stdlib import basekeyed

# Usage format string -- optparse will replace the %prog
usage = "usage: %prog [options]"


class OptionsDict(basekeyed):
    """Make the options object support a mapping interface.
    
    Only attributes defined in the option list passed to this
    class will appear as allowed keys in the mapping. The
    mapping is immutable (since it is only supposed to be
    "assigned" to during option parsing).
    """
    
    def __init__(self, optlist, opts):
        self._optkeys = [optitem[2]['dest'] for optitem in optlist]
        self._opts = opts
    
    def _keylist(self):
        return self._optkeys
    
    def _get_value(self, key):
        return getattr(self._opts, key)
    
    def __getattr__(self, name):
        # Delegate to the underlying options object
        return getattr(self._opts, name)


def _argstring(args):
    if isinstance(args, basestring):
        return args
    # We'd prefer a genexp here but we want to be usable
    # if version < 2.4
    return " ".join(imap(str, args))


def parse_options(optlist, arglist=[]):
    """Convenience function for option parsing.
    
    Adds each option in optlist to the OptionParser and then return
    the parsing results to the program; expects optlist to be a sequence
    of 3-tuples: short name, long name, dict of keyword arguments.
    
    Also checks for correct number of arguments if passed a list of argument
    names in arglist; if arglist is a single string, it is added to the usage
    string but is not used to check the command line.
    """
    
    global usage
    if arglist:
        usage = " ".join([usage, _argstring(arglist)])
    optparser = optparse.OptionParser(usage)
    for shortopt, longopt, kwargs in optlist:
        optparser.add_option(shortopt, longopt, **kwargs)
    opts, args = optparser.parse_args()
    opts = OptionsDict(optlist, opts)
    if not isinstance(arglist, basestring):
        l1 = len(args)
        l2 = len(arglist)
        if l1 != l2:
            optparser.error(
                "Invalid arguments: %i received, %i expected." % (l1, l2))
    return opts, args
