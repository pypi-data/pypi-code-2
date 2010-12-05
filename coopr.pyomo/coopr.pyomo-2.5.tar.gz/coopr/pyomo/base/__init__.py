#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

from numvalue import *
from expr import *
from intrinsic_functions import *
from numtypes import *
from plugin import *
from PyomoModelData import *
#
# Components
#
from component import *
from sets import *
from param import *
from var import *
from constraint import *
from objective import *
#
from set_types import *
from misc import *
from block import *
from PyomoModel import *
#
import pyomo
#
from util import *
from rangeset import *

import sys as _sys  # '_' so it won't be imported by the importing module
if _sys.version_info[0:2] < (2, 5):
    # This is the hack to work around the deepcopy issues that Python 2.4
    # has.  Basically, exhaustively attach a manual __deepcopy__ to classes
    # that need it.
    from pyutilib.misc import create_deepcopy as _cd
    from param import _ParamArray, _ParamValue, _ParamElement
    from var import _VarBase, _VarArray, _VarElement, _VarValue
    from pyutilib.component.core import Plugin

    _to_deepcopy = (
        _ParamArray,
        _ParamElement,
        _ParamValue,
        _VarBase,
        _VarArray,
        _VarElement,
        _VarValue,
        _VirtualSet,
        Block,
        Constraint,
        Model,
        Objective,
        RangeSet,
        RealSet,
        SOSConstraint,
        Var,

        Plugin,
    )
    for _i in _to_deepcopy:
        _i.__deepcopy__ = _cd( _i )

#
# This is a hack to strip out modules, which shouldn't have been included in these imports
#
import types
_locals = locals()
__all__ = [__name for __name in _locals.keys() if (not __name.startswith('_') and not isinstance(_locals[__name],types.ModuleType)) or __name == '_' ]
__all__.append('pyomo')
