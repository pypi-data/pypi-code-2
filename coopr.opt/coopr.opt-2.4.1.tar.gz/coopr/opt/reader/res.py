#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

#
# Class for reading results with the SolverResults object
#

import os
import sys
import re

from coopr.opt.base import results
from coopr.opt.base.formats import *
from coopr.opt import SolverResults
from pyutilib.component.core import alias


class ResultsReader_results(results.AbstractResultsReader):
    """
    Class that reads in a *.results file and generates a 
    SolverResults object.
    """

    alias(str(ResultsFormat.yaml))

    def __init__(self):
        results.AbstractResultsReader.__init__(self,ResultsFormat.yaml)

    def __call__(self, filename, res=None, soln=None):
        """
        Parse a *.results file
        """
        if res is None:
            res = SolverResults()  
        #
        res.read(filename)
        return res

