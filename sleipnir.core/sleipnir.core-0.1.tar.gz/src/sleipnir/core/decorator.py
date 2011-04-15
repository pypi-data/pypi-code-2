#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Decorators"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "LGPL"

# Import Here any required modules for this module.
import __builtin__

from cProfile import Profile
from pstats import Stats
from subprocess import Popen, PIPE
from sys import argv

__all__ = ['profile', ]

# local submodule requirements


#pylint: disable-msg=C0103, R0903
class profile(object):
    """A class decorator which profiles a callable"""

    counter = 0

    def __init__(self, filename=None, standalone=False, dot=True, threshold=1):
        self.standalone = standalone
        self.filename = filename or argv[0]
        self.threshold = threshold
        self.dot = dot
        self.stats = []

    def __call__(self, fun):
        def wrapper(*args, **kwargs):
            """ A wrapper for func"""
            if not getattr(__builtin__, '__profile__', False):
                return fun(*args, **kwargs)

            filename = "".join(self.filename)
            if self.standalone:
                filename = "".join((fun.__name__, str(self.counter),))
                self.counter += 1
            pfilename = "".join((filename, '.profile',))

            # load previous stats
            prof = Profile()
            retv = prof.runcall(fun, *args, **kwargs)
            if pfilename in self.stats:
                stats = Stats(pfilename)
                stats.add(prof)
            else:
                self.stats.append(pfilename)
                stats = Stats(prof)
            stats.dump_stats(pfilename)

            # create profile diagram
            # pylint: disable-msg=W0612, W0702
            if self.dot:
                threshold = self.threshold
                dot = "dot -Tpng -o %(filename)s.png" % locals()
                gprof = "gprof2dot.py -n %(threshold)s -e "\
                    "%(threshold)s -f pstats %(pfilename)s" % locals()
                try:
                    cmd1 = Popen(gprof.split(), stdout=PIPE)
                    cmd2 = Popen(dot.split(), stdin=cmd1.stdout)
                except:
                    pass
            return retv
        # return decorator
        return wrapper
