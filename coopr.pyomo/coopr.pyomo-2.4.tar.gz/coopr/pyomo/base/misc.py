#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['display']

import sys


def display(obj, ostream=None):
    """ Display data in a Pyomo object"""
    if ostream is None:
        ostream = sys.stdout
    try:
        obj.display(ostream=ostream)
    except Exception, err:
        raise TypeError, "Error trying to display values for object of type "+str(type(obj))+": "+str(err)

