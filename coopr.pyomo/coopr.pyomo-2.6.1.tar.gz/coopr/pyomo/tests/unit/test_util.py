#
# Unit Tests for Utility Functions
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")
currdir = dirname(abspath(__file__))+os.sep

import pyutilib.th as unittest
from coopr.pyomo import *
from nose.tools import nottest
import pickle


class TestNumericValue(unittest.TestCase):

    def test_expr1(self):
        model = AbstractModel()
        model.A = Set(initialize=[1,2,3])
        model.B = Param(model.A,initialize={1:100,2:200,3:300})
        model.x = Var(model.A)
        model.y = Var(model.A)
        instance=model.create()
        expr = dot_product(instance.x,instance.B,instance.y)
        OUTPUT=open(currdir+"test_expr1.out","w")
        expr.pprint(ostream=OUTPUT)
        OUTPUT.close()
        self.assertFileEqualsBaseline(currdir+"test_expr1.out",currdir+"test_expr1.txt")

    def test_expr2(self):
        model = AbstractModel()
        model.A = Set(initialize=[1,2,3])
        model.B = Param(model.A,initialize={1:100,2:200,3:300})
        model.x = Var(model.A)
        model.y = Var(model.A)
        instance=model.create()
        expr = dot_product(instance.x,instance.B,instance.y, index=[1,3])
        OUTPUT=open(currdir+"test_expr2.out","w")
        expr.pprint(ostream=OUTPUT)
        OUTPUT.close()
        self.assertFileEqualsBaseline(currdir+"test_expr2.out",currdir+"test_expr2.txt")

    def test_expr3(self):
        model = AbstractModel()
        model.A = Set(initialize=[1,2,3])
        model.B = Param(model.A,initialize={1:100,2:200,3:300})
        model.x = Var(model.A)
        model.y = Var(model.A)
        instance=model.create()
        expr = dot_product(instance.x,instance.B,denom=instance.y, index=[1,3])
        OUTPUT=open(currdir+"test_expr3.out","w")
        expr.pprint(ostream=OUTPUT)
        OUTPUT.close()
        self.assertFileEqualsBaseline(currdir+"test_expr3.out",currdir+"test_expr3.txt")

    def test_expr4(self):
        model = AbstractModel()
        model.A = Set(initialize=[1,2,3])
        model.B = Param(model.A,initialize={1:100,2:200,3:300})
        model.x = Var(model.A)
        model.y = Var(model.A)
        instance=model.create()
        expr = dot_product(denom=[instance.y,instance.x])
        OUTPUT=open(currdir+"test_expr4.out","w")
        expr.pprint(ostream=OUTPUT)
        OUTPUT.close()
        self.assertFileEqualsBaseline(currdir+"test_expr4.out",currdir+"test_expr4.txt")

class TestPickle(pyutilib.th.TestCase):

    def test_p1(self):
        model = AbstractModel()
        model.A = Set(initialize=[1,2,3])
        model.B = Param(model.A,initialize={1:100,2:200,3:300})
        model.x = Var(model.A)
        model.y = Var(model.A)
        str = pickle.dumps(model)
        tmodel = pickle.loads(str)
        instance=tmodel.create()
        expr = dot_product(instance.x,instance.B,instance.y)
        OUTPUT=open(currdir+"test_expr1.out","w")
        expr.pprint(ostream=OUTPUT)
        OUTPUT.close()
        self.assertFileEqualsBaseline(currdir+"test_expr1.out",currdir+"test_expr1.txt")

    def test_p2(self):
        model = AbstractModel()
        model.A = Set(initialize=[1,2,3])
        model.B = Param(model.A,initialize={1:100,2:200,3:300})
        model.x = Var(model.A)
        model.y = Var(model.A)
        tmp=model.create()
        str = pickle.dumps(tmp)
        instance = pickle.loads(str)
        expr = dot_product(instance.x,instance.B,instance.y)
        OUTPUT=open(currdir+"test_expr1.out","w")
        expr.pprint(ostream=OUTPUT)
        OUTPUT.close()
        self.assertFileEqualsBaseline(currdir+"test_expr1.out",currdir+"test_expr1.txt")

    @unittest.skipIf(sys.version_info[:2] < (2,6), "Skipping test because the sparse_dict repn is not supported")
    def test_p3(self):
        def rule1(model):
            return (1,model.x+model.y[1],2)
        def rule2(i,model):
            return (1,model.x+model.y[1]+i,2)

        model = AbstractModel()
        model.a = Set(initialize=[1,2,3])
        model.A = Param(initialize=1)
        model.B = Param(model.a, repn='sparse_dict')
        model.x = Var(initialize=1,within=Reals)
        model.y = Var(model.a, initialize=1,within=Reals)
        model.obj = Objective(rule=lambda model: model.x+model.y[1])
        model.obj2 = Objective(model.a,rule=lambda i,model: i+model.x+model.y[1])
        model.con = Constraint(rule=rule1)
        model.con2 = Constraint(model.a, rule=rule2)
        instance = model.create()
        try:
            str = pickle.dumps(instance)
            self.fail("Expected pickling error due to the use of lambda expressions")
        except pickle.PicklingError:
            pass
        except TypeError:
            pass



if __name__ == "__main__":
   unittest.main()
