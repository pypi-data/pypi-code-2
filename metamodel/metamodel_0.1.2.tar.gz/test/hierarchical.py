from metamodel import SubscribableModel as Model

from metamodel.hierarview import HierarView as View
from metamodel.hierarview import TopHierarView as TopView
class NoView(object):
    def __init__(*args):
        pass
# models
class A(Model):
    pass
class B(Model):
    pass
class C(Model):
    pass
class D(Model):
    pass
class E(Model):
    pass
class F(Model):
    pass
class G(Model):
    pass

# views
class viewG(View):
    pass
class viewF(View):
    _model2view = {'G': [viewG]}

class viewE(View):
    pass

class viewD(NoView):
    pass

class viewC(NoView):
    pass

class viewB(View):
    _model2view = {'E': [viewE],
                   'F': [viewF]}

class viewA(TopView):
    _model2view = {'B': [viewB]}


# ---------------
# a1              [viewA]
#   b1            [viewB]
#     c1          
#        d1       
#           e1    [viewE]
#             g1  
#     c2          
#        f1       [viewF]
#           g2    {viewG}

a1 = A()
b1 = B()
c1 = C()
c2 = C()
d1 = D()
e1 = E()
f1 = F()
g1 = F()
g2 = G()

a1.addChild(b1)
b1.addChild(c1)
b1.addChild(c2)

c1.addChild(d1)

d1.addChild(e1)
c2.addChild(f1)

e1.addChild(g1)
f1.addChild(g2)

ViewA = viewA(a1)

# initial view testing
a_children = ViewA._children_views
assert(len(a_children.values()) == 1)
assert(a_children.values()[0].__class__ == viewB)
b_children = a_children.values()[0]._children_views
b_childclasses = map(lambda s: s.__class__, b_children.values())
assert(len(b_children.values()) == 2)
assert(set(b_childclasses) == set([viewE, viewF]))
f_child = filter(lambda s: s.__class__ == viewF, b_children.values())[0]
assert(len(f_child._children_views.values()) == 1)
assert(f_child._children_views.values()[0].__class__ == viewG)
#ViewA._children_views.values()[0]._children_views
#for bla in ViewA._children_views.values()[0]._children_views.values():
    #    print bla._children_views

# removing nodes
f1.delChild(g2)
assert(len(f_child._children_views.values()) == 0)

try:
    ViewA.getViewNode(f1)
    raise Exception,"Didnt get deleted!"
except:
    # its ok!
    pass

assert(len(b_children.values()) == 2)
c2.delChild(f1)
assert(len(b_children.values()) == 1)

# adding nodes
f2 = F()
c2.addChild(f2)
assert(len(b_children.values()) == 2)
c2.addChild(f1)
assert(len(b_children.values()) == 3)

# test finding child nodes
assert(ViewA.getViewNode(b1) == a_children.values()[0])

