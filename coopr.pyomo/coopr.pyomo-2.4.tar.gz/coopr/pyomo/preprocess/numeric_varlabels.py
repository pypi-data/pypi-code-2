#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the FAST README.txt file.
#  _________________________________________________________________________

import pyutilib.component.core
from coopr.pyomo.base import IPyomoPresolver, IPyomoPresolveAction


class NumericVarLabelsPresolver(pyutilib.component.core.SingletonPlugin):
    """
    This plugin changes variables names to use a simple name that
    uses the variable id.
    """

    pyutilib.component.core.implements(IPyomoPresolveAction)

    def __init__(self, **kwds):
        kwds['name'] = "numeric_varlabels"
        pyutilib.component.core.Plugin.__init__(self, **kwds)

    def rank(self):
        return 1000

    def preprocess(self,model):
        """
        The main routine to perform the preprocess
        """
        for id in model._var:
            model._var[id].label = "x_"+str(id)
            model._name_varmap[model._var[id].label] = model._var[id]
        for id in model._con:
            model._con[id].label = "c_"+str(id)
        return model

