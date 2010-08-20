import inspect
import types
from peak.rules.core import AmbiguousMethods, NoApplicableMethods, intersect
from peak.rules.core import istype
from peak.rules.predicates import meta_function, IsInstance, IsSubclass
from peak.rules.criteria import Disjunction, Class, Test, Signature
from peak.util.assembler import Const

from prioritized_methods import prioritized_when as when,\
                                prioritized_around as around,\
                                prioritized_before as before,\
                                prioritized_after as after,\
                                generic

#from rum.util import issubclass_or_instance

def issubclass_or_instance(obj, cls):
    """
    Returns ``True`` if ``obj`` is a subclass or an instance of ``cls``

    Example::

        >>> class A(object): pass
        >>> class B(A): pass
        >>> issubclass_or_instance(B, A)
        True
        >>> issubclass_or_instance(A(), A)
        True
        >>> issubclass_or_instance(B(), A)
        True
    """
    return isclass(obj) and issubclass(obj, cls) or isinstance(obj, cls)

__all__ = ["generic", "when", "around", "before", "after",
           "NoApplicableMethods", "AmbiguousMethods", "PredicateBuilder"]



#TODO: This should be done with meta_functions
class PredicateBuilder(object):
    def __init__(self, locals_, pred=None):
        self.locals = locals_
        self.locals['isclass'] = inspect.isclass
        self._conditions = []
        if pred:
            self._conditions.append(pred)

    def subclass(self, name, value):
        self.locals['_'+name] = value
        self._conditions.append(
            "isclass(%(name)s) and issubclass(%(name)s, _%(name)s)" % {'name':name}
            )

    def subclass_or_instance(self, name, value):
        self.locals['_'+name] = value
        self._conditions.append(
            "(isclass(%(name)s) and issubclass(%(name)s, _%(name)s)) or isinstance(%(name)s, _%(name)s)" % {'name':name}
            )

    def is_(self, name, value):
        self.locals['_'+name] = value
        self._conditions.append("%(name)s is _%(name)s" % {'name': name})

    def equals(self, name, value):
        self.locals['_'+name] = value
        self._conditions.append("%(name)s == _%(name)s" % {'name': name})
    
    def equals_or_none(self, name, value):
        self.locals['_'+name] =value
        self._conditions.append("(%(name)s is None) or (%(name)s == _%(name)s)" % {'name': name})
    
    @property
    def predicate(self):
        if self._conditions:
            return ' and '.join("(%s)"%c for c in self._conditions)
        return ()



#XXX: We can only handle new-style classes since the disjunction creates
#     ambiguous methodfs when it shouldn't. Is this a bug in peak.rules?
#class_types = Disjunction([Class(type), Class(types.ClassType)])
class_types = Class(type)

# Optimized isclass tests,
# see http://www.eby-sarna.com/pipermail/peak/2008-July/003012.html
@meta_function(inspect.isclass)
def compile_isclass(obj):
    ret =  Test(IsInstance(obj), class_types) 
    return ret

#if False:
#    @meta_function(issubclass_or_instance)
#    def compile_issubclass_or_instance(__builder__, obj, cls):
#        """
#            >>> from peak.rules import when
#            >>> class A(object): pass
#            >>> def f(obj): pass
#
#            >>> _ = when(f, "issubclass_or_instance(obj, A)")(lambda obj: True)
#            >>> _ = when(f, "not issubclass_or_instance(obj, A)")(lambda obj: False)
#
#            >>> assert f(A)
#            >>> assert f(A())
#
#            >>> class SubA(A): pass
#            >>> assert f(SubA)
#            >>> assert f(SubA())
#
#            >>> class B(object): pass
#            >>> assert not f(B)
#            >>> assert not f(B())
#        """
#        return Disjunction([
#            Signature([
#                Test(IsInstance(obj), Class(type)),
#                Test(IsSubclass(obj), Class(cls)),
#                ]),
#            Test(IsInstance(obj), Class(cls)),
#            ])
#
#    def compile_issubclass_or_instance2(__builder__, obj, cls):
#        __builder__.push({
#            'obj': obj,
#            'cls': cls,
#            'class_types': Const((type,types.ClassType)),
#            'issubclass': Const(issubclass),
#            'isinstance': Const(isinstance),
#            })  
#        result = __builder__.parse(
#            "isinstance(obj, class_types) and issubclass(obj, cls) or "
#            "isinstance(obj, cls)"
#            )
#        __builder__.pop()
#        return result
#
