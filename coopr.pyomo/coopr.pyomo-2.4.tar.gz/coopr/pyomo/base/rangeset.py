#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['RangeSet']

import sets
import expr
from numvalue import value
from pyutilib.component.core import *

class RangeSetValidator(object):

    def __init__(self, start, end, step):
        self.start=start
        self.end=end
        self.step=step

    def __call__(self,val,model):
       if val < self.start:
          return False
       if val > self.end:
          return False
       if (val-self.start)%self.step != 0:
          return False
       return True


class RangeSet(sets._SetContainer):
    """A set that represents a list of integer values"""

    alias("RangeSet", "A sequence of numeric values.  RangeSet(start,end,step) is a sequence starting a value 'start', and increasing in values by 'step' until a value greater than of equal to 'end' is reached.")

    def __init__(self,*args,**kwds):
        """Construct a list of integers"""
        if kwds.pop('_deep_copying', None):
            # Hack for Python 2.4 compatibility
            # Deep copy will copy all items as necessary, so no need to
            # complete parsing
            return

        tmp=()
        sets._SetContainer.__init__(self,*tmp,**kwds)
        self._type=RangeSet
        self.ordered=True
        if len(args) == 1:
           self._start=1
           self._end=args[0]
           self._step=1
        elif len(args) == 2:
           self._start=args[0]
           self._end=args[1]
           self._step=1
        else:
           self._start=args[0]
           self._end=args[1]
           self._step=args[2]

    def construct(self, values=None):
        if self._constructed:
            return
        self._constructed=True
        if isinstance(self._start,expr.Expression):
           self._start_val = self._start()
        else:
           self._start_val = value(self._start)

        if isinstance(self._end,expr.Expression):
           self._end_val = self._end()
        else:
           self._end_val = value(self._end)

        if isinstance(self._step,expr.Expression):
           self._step_val = self._step()
        else:
           self._step_val = value(self._step)

        if self.validate is None:
           self.validate=RangeSetValidator(self._start_val, self._end_val, self._step_val)

        #
        # Generate set, and track the bounds
        #
        lb = self._start_val
        ub = self._start_val
        for val in xrange(self._start_val, self._end_val+1, self._step_val):
          if self._verify(val,False):
             ub=val
             self.add(val)

        #
        # Apply the filter, if present
        #
        if self.filter is not None:
            self._apply_filter()
            lb = min(self.value)
            ub = max(self.value)

        # Assign bounds
        self._bounds=(lb,ub)
