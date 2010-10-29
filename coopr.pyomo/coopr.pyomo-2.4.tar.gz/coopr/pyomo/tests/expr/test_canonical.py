#
# Test the canonical expressions 
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+os.sep+".."+os.sep+"..")
currdir = dirname(abspath(__file__))+os.sep

from coopr.pyomo import *
from coopr.opt import *
#from coopr.pyomo.base.var import _VarElement
import pyutilib.th as unittest
import pyutilib.services
from coopr.pyomo.preprocess.simple_preprocessor import SimplePreprocessor
from pyutilib.component.core import PluginGlobals

class frozendict(dict):
    __slots__ = ('_hash',)
    def __hash__(self):
        rval = getattr(self, '_hash', None)
        if rval is None:
            rval = self._hash = hash(frozenset(self.iteritems()))
        return rval


class TestBase(unittest.TestCase):

    def setUp(self):
        self.model = Model()

    def construct(self,filename):
        self.instance = self.model.create(filename)


class Test(TestBase):

    def setUp(self):
        #
        # Create Model
        #
        TestBase.setUp(self)
        #PluginGlobals.pprint()
        self.plugin = SimplePreprocessor()
        self.plugin.deactivate_action("compute_canonical_repn")

    def tearDown(self):
        if os.path.exists("unknown.lp"):
           os.unlink("unknown.lp")
        pyutilib.services.TempfileManager.clear_tempfiles()
        self.plugin.activate_action("compute_canonical_repn")

    def test_expr1(self):
        self.model.A = RangeSet(1,4)
        def p_init(i, model):
            return 2*i
        self.model.p = Param(self.model.A, initialize=p_init)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return summation(model.p, model.x)
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        #self.instance.obj[None].expr.pprint()
        mid=id(self.instance)
        rep = generate_canonical_repn(self.instance.obj[None].expr)
        del rep[-1]
        self.failUnlessEqual(rep, {1: {frozendict({(mid,2): 1}): 6.0, frozendict({(mid,1): 1}): 4.0, frozendict({(mid,3): 1}): 8.0, frozendict({(mid,0): 1}): 2.0}})

    def test_expr2(self):
        self.model.A = RangeSet(1,4)
        def p_init(i, model):
            return 2*i
        self.model.p = Param(self.model.A, initialize=p_init)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return summation(model.x, model.p)
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        mid=id(self.instance)
        #self.instance.obj[None].expr.pprint()
        rep = generate_canonical_repn(self.instance.obj[None].expr)
        del rep[-1]
        self.failUnlessEqual(rep, {1: {frozendict({(mid,2): 1}): 6.0, frozendict({(mid,1): 1}): 4.0, frozendict({(mid,3): 1}): 8.0, frozendict({(mid,0): 1}): 2.0}})

    def test_expr3(self):
        self.model.A = RangeSet(1,4)
        def p_init(i, model):
            return 2*i
        self.model.p = Param(self.model.A, initialize=p_init)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return 2*model.x[1] + 3*model.x[1] + 4*(model.x[1]+model.x[2])
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        mid=id(self.instance)
        #self.instance.obj[None].expr.pprint()
        rep = generate_canonical_repn(self.instance.obj[None].expr)
        del rep[-1]
        self.failUnlessEqual(rep,
                    {1: {frozendict({(mid,0): 1}):9.0, frozendict({(mid,1): 1}):4.0}})

    def test_expr4(self):
        self.model.A = RangeSet(1,4)
        def p_init(i, model):
            return 2*i
        self.model.p = Param(self.model.A, initialize=p_init)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return 1.2 + 2*model.x[1] + 3*model.x[1]
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        mid=id(self.instance)
        #self.instance.obj[None].expr.pprint()
        rep = generate_canonical_repn(self.instance.obj[None].expr)
        del rep[-1]
        self.failUnlessEqual(rep, {0:frozendict({None:1.2}), 1: {frozendict({(mid,0): 1}): 5.0}})

    def test_expr5(self):
        self.model.A = RangeSet(1,4)
        def p_init(i, model):
            return 2*i
        self.model.p = Param(self.model.A, initialize=p_init)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return model.x[1]*(model.x[1]+model.x[2]) + model.x[2]*(model.x[1]+3.0*model.x[3]*model.x[3])
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        mid=id(self.instance)
        #self.instance.obj[None].expr.pprint()
        rep = generate_canonical_repn(self.instance.obj[None].expr)
        del rep[-1]
        self.failUnlessEqual(rep,
                {2: {frozendict({(mid,0):2}):1.0, frozendict({(mid,0):1, (mid,1):1}):2.0}, 3:{frozendict({(mid,1):1, (mid,2):2}):3.0}})

    def test_expr6(self):
        self.model.A = RangeSet(1,4)
        def p_init(i, model):
            return 2*i
        self.model.p = Param(self.model.A, initialize=p_init)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return 2.0*(1.2 + 2*model.x[1] + 3*model.x[1]) + 3.0*(1.0+model.x[1])
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        mid=id(self.instance)
        #self.instance.obj[None].expr.pprint()
        rep = generate_canonical_repn(self.instance.obj[None].expr)
        del rep[-1]
        self.failUnlessEqual(rep,
            {0:frozendict({None:5.4}), 1: {frozendict({(mid,0): 1}): 13.0}})

    def test_expr7(self):
        self.model.A = RangeSet(1,4)
        def p_init(i, model):
            return 2*i
        self.model.p = Param(self.model.A, initialize=p_init)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return summation(model.p, model.x)/2.0
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        mid=id(self.instance)
        #self.instance.obj[None].expr.pprint()
        rep = generate_canonical_repn(self.instance.obj[None].expr)
        del rep[-1]
        self.failUnlessEqual(rep,
            {1: {frozendict({(mid,2): 1}): 3.0, frozendict({(mid,1): 1}): 2.0, frozendict({(mid,3): 1}): 4.0, frozendict({(mid,0): 1}): 1.0}})

    def test_expr8(self):
        self.model.A = RangeSet(1,4)
        def p_init(i, model):
            return 2*i
        self.model.p = Param(self.model.A, initialize=p_init)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        self.model.y = Var(initialize=2.0)
        def obj_rule(model):
            return summation(model.p, model.x)/model.y
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        self.instance.y.fixed = True
        self.instance.y.reset()
        mid=id(self.instance)
        #self.instance.obj[None].expr.pprint()
        rep = generate_canonical_repn(self.instance.obj[None].expr)
        del rep[-1]
        self.failUnlessEqual(rep,
            {1: {frozendict({(mid,2): 1}): 3.0, frozendict({(mid,1): 1}): 2.0, frozendict({(mid,3): 1}): 4.0, frozendict({(mid,0): 1}): 1.0}})

    def test_expr9(self):
        self.model.A = RangeSet(1,4)
        def p_init(i, model):
            return 2*i
        self.model.p = Param(self.model.A, initialize=p_init)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        self.model.y = Var(initialize=1.0)
        def obj_rule(model):
            return summation(model.p, model.x)/(1+model.y)
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        self.instance.y.fixed = True
        self.instance.y.reset()
        mid=id(self.instance)
        #self.instance.obj[None].expr.pprint()
        rep = generate_canonical_repn(self.instance.obj[None].expr)
        del rep[-1]
        self.failUnlessEqual(rep,
            {1: {frozendict({(mid,2): 1}): 3.0, frozendict({(mid,1): 1}): 2.0, frozendict({(mid,3): 1}): 4.0, frozendict({(mid,0): 1}): 1.0}})

    def test_expr10(self):
        self.model.A = RangeSet(1,4)
        def p_init(i, model):
            return 2*i
        self.model.p = Param(self.model.A, initialize=p_init)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        self.model.y = Var(initialize=1.0)
        def obj_rule(model):
            return summation(model.p, model.x)/(1+model.y)
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        #self.instance.obj[None].expr.pprint()
        rep = generate_canonical_repn(self.instance.obj[None].expr)
        self.failUnless(len(rep) == 1 and None in rep)

    def test_expr11(self):
        self.model.A = RangeSet(1,4)
        def p_init(i, model):
            return 2*i
        self.model.p = Param(self.model.A, initialize=p_init)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        self.model.y = Var(initialize=1.0)
        def obj_rule(model):
            return (1.0+model.x[1]+1/model.x[2]) + (2.0+model.x[2]+1/model.x[3])
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        #self.instance.obj[None].expr.pprint()
        rep = generate_canonical_repn(self.instance.obj[None].expr)
        rep[None].pprint()
        del rep[None]
        del rep[-1]
        mid=id(self.instance)
        self.failUnlessEqual(rep, {0: {None: 3.0}, 1: {frozendict({(mid,1): 1}): 1.0, frozendict({(mid,0): 1}): 1.0}})

    def test_expr12(self):
        self.model.A = RangeSet(1,4)
        def p_init(i, model):
            return 2*i
        self.model.p = Param(self.model.A, initialize=p_init)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        self.model.y = Var(initialize=1.0)
        def obj_rule(model):
            return (1.0+model.x[1]+1/model.x[2]) * (2.0+model.x[2]+1/model.x[3])
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        mid=id(self.instance)
        #self.instance.obj[None].expr.pprint()
        rep = generate_canonical_repn(self.instance.obj[None].expr)
        rep[None].pprint()
        del rep[None]
        del rep[-1]
        self.failUnlessEqual(rep, {0: {None: 2.0}, 1: {frozendict({(mid,1): 1}): 1.0, frozendict({(mid,0): 1}): 2.0}, 2: {frozendict({(mid,0): 1, (mid,1): 1}): 1.0}})

if __name__ == "__main__":
   unittest.main()

