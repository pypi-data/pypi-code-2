#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['SolverResults', 'SolverStatus', 'ProblemSense', 'SolutionStatus', 'Solution']

from pyutilib.misc import format_io
from pyutilib.math import as_number
from pyutilib.enum import Enum

import sys
import StringIO

SolverStatus = Enum('error', 'warning', 'ok', 'aborted')
ProblemSense = Enum('unknown', 'minimize', 'maximize')
SolutionStatus = Enum('unbounded', 'globallyOptimal', 'locallyOptimal',
                            'optimal', 'bestSoFar', 'feasible', 'infeasible',
                            'stoppedByLimit', 'unsure', 'error', 'other')


class _SolutionSuffix(object):

    def __init__(self, description):
        self._info = []
        self._index = {}
        self._count = {}
        self.description = description

    def add(self, index, value):
        """ NOTE: this function is deprecated """
        self.__setitem__(index, value)

    def __getitem__(self, key):
        if isinstance(key,basestring):
            return self._index[key]
        return self._count[key]

    def __setitem__(self, index, value):
        if isinstance(index, basestring):
            index = index.replace('(','[')
            index = index.replace(')',']')
        if type(value) is str:
           tmp = eval(value)
        else:
           tmp = value
        self._count[len(self._info)]=tmp
        self._info.append( (index, tmp) )
        self._index[index]=tmp
        #
        # If the index has the format x(1,a) or x[3,4,5]
        # then create a dictionary attribute 'x', which maps
        # the tuple values to the corresponding value.
        #
        if isinstance(index, basestring):
            if '[' in index:
                pieces = index.split('[')
                name = pieces[0]
                rest = None
                # when a variable is indexed by more than one parameter, you will
                # see identifiers of the form "x((a,b))" instead of the "x(a)"
                # one-dimensional form. this is due to the process of "stringifying"
                # the index, which is fine. it just requires a bit of ugliness in
                # the string splitting process.
                if index.count("]") == 2:
                   rest = pieces[2]
                else:
                   rest = pieces[1]
                # we're always taking the first part of the index,
                # so even in the two (or greater) dimensional case
                # such as "x((a,b))", the first piece is what we want.
                tpl = rest.split(']')[0]
                tokens = tpl.split(',')
                for i in xrange(len(tokens)):
                    tokens[i] = as_number(tokens[i])
                try:
                    var = getattr(self, name)
                except Exception, err:
                    setattr(self, name, {})
                    var = getattr(self, name)
                if len(tokens) == 1:
                    var[ tokens[0] ] = tmp
                else:
                    var[ tuple(tokens) ] = tmp
            else:
                setattr(self, index, tmp)
            
            

    def __len__(self):
        return len(self._info)

    def __iter__(self):
        return self._info.__iter__()

    def pprint(self, ostream=None, symbol_map=None):
        if ostream is None:
           ostream = sys.stdout
        if len(self._info) != 0:
           print >>ostream, "  "+self.description
           flag=True
           for (name,value) in self._info:
              # translate the name, if a map is available and the
              # item is in the map.
              if (symbol_map is not None) and (name in symbol_map):
                 name=symbol_map[name]
              if value != 0:
                 print >>ostream, "        "+str(name)+"\t"+format_io(value)
                 flag=False
           if flag:
              print >>ostream,   "        No nonzero values"


class Solution(object):

    def __init__(self):
        self.__dict__["_suffix"] = []
        self.value = None
        self.gap = None
        self.status = SolutionStatus.unsure
        self.add_suffix("variable","Primal Variables")
        self.add_suffix("dual","Dual Variables")
        self.add_suffix("slack","Constraint Slacks")
        self.add_suffix("constraint","Constraint Values")

    def __getattr__(self, name):
        try:
            if name in self.__dict__['_suffix']:
                return self.__dict__["_"+name]
        except KeyError:
            pass
        try:
           return self.__dict__[name]
        except KeyError:
           raise AttributeError, "Unknown attribute "+str(name)

    def __setattr__(self, name, val):
        if name in self._suffix:
           raise AttributeError, "Cannot set attribute '"+name+"' which is reserved for suffix array"
        self.__dict__[name]=val

    def add_suffix(self,name,description):
        self._suffix.append(name)
        setattr(self, "_"+name, _SolutionSuffix(description))

    def pprint(self, ostream=None, only_variables=False, symbol_map=None):
        if ostream is None:
           ostream = sys.stdout
        print >>ostream, "----------------------------------------------------------"
        print >>ostream, "------  Solution "+ str(self._counter+1)
        print >>ostream, "----------------------------------------------------------"
        tmp = self.__dict__.keys()
        tmp.sort()
        for key in tmp:
          if key[0] != "_":
             if key != "value":
                print >>ostream, " ",key+":", format_io(getattr(self, key))
             else:
                tmp = getattr(self,key)
                if isinstance(tmp, dict):
                   print >>ostream, "  Objectives"
                   for vkey in tmp:
                     print >>ostream, "        "+str(vkey)+"\t"+format_io(tmp[vkey])
                else:
                   print >>ostream, "  value:",format_io(tmp)
                   
        for item in self._suffix:
            if only_variables and item != "variable":
                continue
            getattr(self,"_"+item).pprint(ostream=ostream, symbol_map=symbol_map)


class SolutionSet(object):

    def __init__(self):
        self._solution={}
        self._counter=0
        self._ndx=[]

    def __len__(self):
        return len(self._solution)

    def __getitem__(self,i):
        return self._solution[i]

    def __call__(self,i=0):
        return self._solution[self._ndx[i]]

    def create(self):
        tmp = Solution()
        self.insert(tmp)
        return tmp

    def insert(self,solution):
        solution._counter = self._counter
        self._solution[self._counter] = solution
        self._ndx.append(self._counter)
        self._counter += 1

    def delete(self,i):
        del self._solution[i]
        self._ndx.remove(i)


class _Data_Container(object):
    pass


class SolverResults(object):

    def __init__(self):
        self.solver = _Data_Container()
        self.problem = _Data_Container()
        self.solution = SolutionSet()
        self.initialize()
        self.symbol_map = None 

    def initialize(self):
        #
        # Standard solver information
        #
        self.solver.status=SolverStatus.ok
        self.solver.systime=None
        self.solver.usrtime=None
        #
        # Standard problem information
        #
        self.problem.name=None
        self.problem.sense=ProblemSense.unknown
        self.problem.num_variables=None
        self.problem.num_constraints=None
        self.problem.num_objectives=None
        self.problem.lower_bound=None
        self.problem.upper_bound=None

    def __str__(self):
        output = StringIO.StringIO()
        self.write(ostream=output, num=sys.maxint)
        return output.getvalue()
        
    def write(self, filename=None, num=1, ostream=None, times=True, only_variables=False):
        if ostream is None:
           ostream = sys.stdout
        if not filename is None:
           OUTPUT=open(filename,"w")
           self.write(num=num,ostream=OUTPUT,times=times)
           OUTPUT.close()
           return

        print >>ostream, "=========================================================="
        print >>ostream, "---  Solver Results                                    ---"
        print >>ostream, "=========================================================="
        print >>ostream, "----------------------------------------------------------"
        print >>ostream, "------  Problem Information                         ------"
        print >>ostream, "----------------------------------------------------------"
        flag=False
        tmp = self.problem.__dict__.keys()
        tmp.sort()
        for key in tmp:
          if key[0] != "_":
             print >>ostream, " ",key+":", format_io(getattr(self.problem, key))
             flag=True
        if not flag:        # pragma:nocover
           print >>ostream, "  No Info"
        if self.symbol_map is not None:
           print >>ostream, "  Symbol map is available"
        #
        print >>ostream, "----------------------------------------------------------"
        print >>ostream, "------  Solver Information                          ------"
        print >>ostream, "----------------------------------------------------------"
        flag=False
        tmp = self.solver.__dict__.keys()
        tmp.sort()
        for key in tmp:
          if key[0] != "_":
             if times or not key in ["systime","usrtime"]:
                print >>ostream, " ",key+":", format_io(getattr(self.solver, key))
             flag=True
        if not flag:        # pragma:nocover
           print >>ostream, "  No Info"
        #
        if not num is None:
           print >>ostream, "  num_solutions: "+str(len(self.solution))
           i=0
           while i<min(num, len(self.solution)):
             self.solution(i).pprint(ostream, only_variables=only_variables, symbol_map=self.symbol_map)
             i += 1
        else:
           print >>ostream, "  num_solutions to display: 0"
        print >>ostream, "----------------------------------------------------------"

    def read(self, filename=None):          #pragma:nocover
        raise IOError, "SolverResults.read is not defined!"

