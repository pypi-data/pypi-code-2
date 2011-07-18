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

import logging
import sys

logger = logging.getLogger('coopr.pyomo')


def display(obj, ostream=None):
    """ Display data in a Pyomo object"""
    if ostream is None:
        ostream = sys.stdout
    try:
        obj.display(ostream=ostream)
    except Exception, err:
        raise TypeError, "Error trying to display values for object of type "+str(type(obj))+": "+str(err)


def create_name(name, ndx):
    if ndx is None:
        return name
    if type(ndx) is tuple:
        tmp = str(ndx).replace(', ',',')
        return name+"["+tmp[1:-1]+"]"
    return name+"["+str(ndx)+"]"


def apply_indexed_rule(obj, rule, model, index):
    if index.__class__ is tuple:
        try:
            expr = rule(model, *index)
        except:
            try:
                expr = rule(*( index + (model,) ))
                logger.warning( "DEPRECATION WARNING: Detected pre-3.0 style "
                                "rule where the model argument appears last "
                                "(%s %s)" % ( obj.__class__.__name__,
                                              create_name(obj.name, index) ) )
            except:
                # Re-run new style and allow exception to propagate
                expr = rule(model, *index)
    else:
        try:
            expr = rule(model, index)
        except:
            try:
                expr = rule(index, model)
                logger.warning( "DEPRECATION WARNING: Detected pre-3.0 style "
                                "rule where the model argument appears last "
                                "(%s %s)" % ( obj.__class__.__name__,
                                              create_name(obj.name, index) ) )
            except:
                # Re-run new style and allow exception to propagate
                expr = rule(model, index)
    return expr

def apply_parameterized_indexed_rule(obj, rule, model, param, index):
    if index.__class__ is tuple:
        try:
            expr = rule(model, param, *index)
        except:
            try:
                expr = rule(*( index + (param, model,) ))
                logger.warning( "DEPRECATION WARNING: Detected pre-3.0 style "
                                "rule where the model argument appears last "
                                "(%s %s)" % ( obj.__class__.__name__,
                                              create_name(obj.name, index) ) )
            except:
                # Re-run new style and allow exception to propagate
                expr = rule(model, param, *index)
    else:
        try:
            expr = rule(model, param, index)
        except:
            try:
                expr = rule(index, param, model)
                logger.warning( "DEPRECATION WARNING: Detected pre-3.0 style "
                                "rule where the model argument appears last "
                                "(%s %s)" % ( obj.__class__.__name__,
                                              create_name(obj.name, index) ) )
            except:
                # Re-run new style and allow exception to propagate
                expr = rule(model, param, index)
    return expr
