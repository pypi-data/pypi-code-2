#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['SolverResults']

import sys
from container import *
from pyutilib.enum import Enum
from pyutilib.misc import Bunch
import copy

import StringIO

import problem
import solver
import solution


try:
    import yaml
    yaml_available=True
except ImportError:
    yaml_available=False


class SolverResults(MapContainer):

    undefined = undefined 
    default_print_options = solution.default_print_options

    def __init__(self):
        MapContainer.__init__(self)
        self._sections = []
        self.symbol_map = None
        self._descriptions = {}
        self.add('problem', ListContainer(problem.ProblemInformation), False, "Problem Information")
        self.add('solver', ListContainer(solver.SolverInformation), False, "Solver Information")
        self.add('solution', solution.SolutionSet(), False, "Solution Information")

    def add(self, name, value, active, description):
        self.declare(name, value=value, active=active)
        tmp = self._convert(name)
        self._sections.append(tmp)
        self._descriptions[tmp]=description

    def yaml_repn(self, options=None):
        if options is None:
            return self._repn_(SolverResults.default_print_options)
        else:
            return self._repn_(options)
        
    def _repn_(self, option):
        if not option.schema and not self._active and not self._required:
            return ignore
        tmp = {}
        for key in self._sections:
            rep = dict.__getitem__(self, key)._repn_(option)
            if not rep == ignore:
                tmp[key] = rep
        return tmp

    def Xwrite(self, **kwds):
        if 'ostream' in kwds:
            ostream = kwds['ostream']
            del kwds['ostream']
        else:
            ostream = sys.stdout
        if 'filename' in kwds:
            OUTPUT=open(kwds['filename'],"w")
            del kwds['filename']
            kwds['ostream']=OUTPUT
            self.write(**kwds)
            OUTPUT.close()
            return

        option = copy.copy(solution.default_print_options)
        for key in kwds:
            setattr(option,key,kwds[key])

        repn = self._repn_(option)
        print >>ostream, "# =========================================================="
        print >>ostream, "# = Solver Results                                         ="
        print >>ostream, "# =========================================================="
        for item in repn:
            key = item.keys()[0]
            print >>ostream, "# ----------------------------------------------------------"
            print >>ostream, "#   %s" % self._descriptions[key]
            print >>ostream, "# ----------------------------------------------------------"
            #print repr(item)
            yaml.dump(item, ostream, default_flow_style=False) 

    def write(self, **kwds):
        if 'ostream' in kwds:
            ostream = kwds['ostream']
            del kwds['ostream']
        else:
            ostream = sys.stdout
        if 'filename' in kwds:
            OUTPUT=open(kwds['filename'],"w")
            del kwds['filename']
            kwds['ostream']=OUTPUT
            self.write(**kwds)
            OUTPUT.close()
            return

        option = copy.copy(SolverResults.default_print_options)
        for key in kwds:
            setattr(option,key,kwds[key])

        repn = self._repn_(option)
        print >>ostream, "# =========================================================="
        print >>ostream, "# = Solver Results                                         ="
        print >>ostream, "# =========================================================="
        for i in xrange(len(self._order)):
            key = self._order[i]
            if not key in repn:
                continue
            item = dict.__getitem__(self,key)
            print >>ostream, ""
            print >>ostream, "# ----------------------------------------------------------"
            print >>ostream, "#   %s" % self._descriptions[key]
            print >>ostream, "# ----------------------------------------------------------"
            print >>ostream, key+":",
            if isinstance(item, ListContainer):
                item.pprint(ostream, option, prefix="", repn=repn[key])
            else:
                item.pprint(ostream, option, prefix="  ", repn=repn[key])

    def read(self, **kwds):
        if not yaml_available:
            raise IOError, "Aborting SolverResults.read() because PyYAML is not installed!"

        if 'istream' in kwds:
            istream = kwds['istream']
            del kwds['istream']
        else:
            ostream = sys.stdin
        if 'filename' in kwds:
            INPUT=open(kwds['filename'],"r")
            del kwds['filename']
            kwds['istream']=INPUT
            self.read(**kwds)
            INPUT.close()
            return

        repn = yaml.load(istream, Loader=yaml.SafeLoader)
        for i in xrange(len(self._order)):
            key = self._order[i]
            if not key in repn:
                continue
            item = dict.__getitem__(self,key)
            item.load(repn[key])
       
    def __repr__(self):
        return str(self._repn_(SolverResults.default_print_options))

    def __str__(self):
        ostream = StringIO.StringIO()
        option=SolverResults.default_print_options
        self.pprint(ostream, option, repn=self._repn_(option))
        return ostream.getvalue()

 

        


if __name__ == '__main__':
    results = SolverResults()
    results.write(schema=True)
    #print results
