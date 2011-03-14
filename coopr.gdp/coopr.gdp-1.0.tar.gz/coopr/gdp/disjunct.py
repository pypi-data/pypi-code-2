#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the FAST README.txt file.
#  _________________________________________________________________________

from coopr.pyomo import *
from coopr.pyomo.base.sets import _BaseSet
from pyutilib.component.core import alias
from pyutilib.misc.indent_io import StreamIndenter

import logging
logger = logging.getLogger('coopr.pyomo')

class GDP_Error(Exception):
    """Exception raised while processing GDP Models"""


class Disjunct(Block):
    alias("Disjunct", "Disjunctive blocks in a model.")

    def __init__(self, *args, **kwargs):
        if kwargs.pop('_deep_copying', None):
            # Hack for Python 2.4 compatibility
            # Deep copy will copy all items as necessary, so no need to
            # complete parsing
            return

        self._rule = kwargs.pop('rule', None )
        self._data = {}
        self._constructed = False
        self._M = None

        kwargs.setdefault('ctype', Disjunct)
        Block.__init__(self, *args, **kwargs)

        self.indicator_var = Var(within=Binary)

        #if ( kwargs ): # if dict not empty, there's an error.  Let user know.
        #    msg = "Creating disjunct '%s': unknown option(s)\n\t%s"
        #    msg = msg % ( self.name, ', '.join(kwargs.keys()) )
        #    raise ValueError, msg

    def __len__(self):
        return len(self._data.keys())

    def keys(self):
        return self._data.keys()
        #return self._index

    def __contains__(self,ndx):
        return ndx in self._data
        #return ndx in self._index

    def __getitem__(self, ndx):
        """This method returns a Disjunct object.
        """
        if ndx in self._data:
            return self._data[ndx]
        msg = "Unknown index in disjunct '%s': %s"
        raise KeyError, msg % ( self.name, str(ndx) )

    def clear(self):
        self._data = {}

    def construct(self, data=None):
        if __debug__ and logger.isEnabledFor(logging.DEBUG):
            logger.debug("Constructing disjunct %s", self.name)
        if self._rule is None:
            if self._no_rule_init is None:
                logger.warn("No construction rule or expression "
                            "specified for disjunct '%s'", self.name)
            return
        if self._constructed:
            return
        self._constructed=True

        #
        # Local variables for code optimization
        #
        _self_rule = self._rule

        def _generate_name(idx):
            if type(idx) in (tuple, list):
                return '['+','.join([_generate_name(x) for x in idx])+']'
            else:
                return str(idx)

        for val in self._index:
            name = _generate_name(val)
            if __debug__ and logger.isEnabledFor(logging.DEBUG):
                logger.debug("   Constructing disjunct index %s", str(name))
            if val is None:
                _self_rule(self, self.model)
            else:
                block = Disjunct()
                self._add_component(name, block)
                if type(val) is tuple:
                    tmp=list(val)
                else:
                    tmp=[val]
                tmp.append(block)
                tmp.append(self.model)
                tmp=tuple(tmp)
                
                _self_rule(*tmp)
                for tmp in block.components.itervalues():
                    tmp.construct(None)
                self._data[val] = block
        #self._index=constructed_indices
        

    def pprint(self, ostream=None):
        if ostream is None:
           ostream = sys.stdout
        print >>ostream, "   ",self.name,":",
        print >>ostream, "\tSize="+str(len(self._data.keys())),
        if isinstance(self._index,_BaseSet):
           print >>ostream, "\tIndex=",self._index.name
        else:
           print >>ostream,""
        if self._M is not None:
            print >>ostream, "\tM=", self._M
        indent = StreamIndenter(ostream)
        if len(self._data):
            for val in self._data.itervalues():
                val.pprint(indent)
        else:
            Block.pprint(self,ostream=indent)

    def next_M(self):
        if self._M is None:
            return None
        elif isinstance(self._M, list):
            if len(self._M):
                return self._M.pop(0)
            else:
                return None
        else:
            return self._M

    def add_M(self, M):
        if self._M is None:
            self._M = M
        elif isinstance(self._M, list):
            self._M.append(M)
        else:
            self._M = [self._M, M]

    def set_M(self, M_list):
        if self._M is not None:
            logger.warn("Discarding pre-defined M values for %s", self.name)
        self._M = M_list

class Disjunction(Constraint):
    alias("Disjunction", "Disjunction expressions in a model.")

    def __init__(self, *args, **kwargs):
        if kwargs.pop('_deep_copying', None):
            # Hack for Python 2.4 compatibility
            # Deep copy will copy all items as necessary, so no need to
            # complete parsing
            return

        tmpname = kwargs.get('name', 'unknown')
        self._disjunction_rule = kwargs.pop('rule', None)
        self._disjunctive_set = kwargs.pop('expr', None)
        self._disjuncts = {}

        kwargs.setdefault('ctype', Disjunction)
        kwargs['rule'] = _disjunctiveRuleMapper(self)
        Constraint.__init__(self, *args, **kwargs)

        if self._disjunction_rule is not None and \
                self._disjunctive_set is not None:
            msg = "Creating disjunction '%s' that specified both rule " \
                "and expression" % tmpname
            raise ValueError, msg
        #if ( kwargs ): # if dict not empty, there's an error.  Let user know.
        #    msg = "Creating disjunction '%s': unknown option(s)\n\t%s"
        #    msg = msg % ( tmpname, ', '.join(kwargs.keys()) )
        #    raise ValueError, msg

class _disjunctiveRuleMapper(object):
    def __init__(self, disjunction):
        self.disj = disjunction

    def __call__(self, *args):
        model = args[-1]
        idx = args[0:-1]
        if len(idx)>1 and idx not in self.disj._index:
            logger.warn("Constructing disjunction from "
                        "unrecognized index: %s", str(idx))
        elif len(idx) == 1 and idx[0] not in self.disj._index:
            logger.warn("Constructing disjunction from "
                        "unrecognized index: %s", str(idx[0]))

        if self.disj._disjunction_rule is not None:
            tmp = list(args)
            #tmp.append(self.disj)
            tmp = tuple(tmp)
            disjuncts = self.disj._disjunction_rule(*tmp)
        elif type(self.disj._disjunctive_set) in (tuple, list):
            # explicit disjunction over a user-specified list of disjuncts
            disjuncts = self.disj._disjunctive_set
        elif isinstance(self.disj._disjunctive_set, Disjunct):
            # pick one of all disjuncts
            if len(self.disj._disjunctive_set._data):
                disjuncts = self.disj._data.values()
            else:
                disjuncts = ( self.disj._disjunctive_set )
        else:
            msg = 'Bad expression passed to Disjunction'
            raise TypeError, msg
        
        for d in disjuncts:
            if not isinstance(d, Disjunct):
                msg = 'Non-disjunct (type="%s") found in ' \
                    'disjunctive set for disjunction %s' % \
                    ( type(d), self.disj.name )
                raise ValueError, msg
            if len(d._data):
                msg = 'Disjunct in disjunctive set is specified ' \
                    'over an index'
                raise IndexError, msg

        self.disj._disjuncts[tuple(idx)] = disjuncts
        # sum(disjuncts) == 1
        return (sum(d.indicator_var for d in disjuncts), 1.0)
