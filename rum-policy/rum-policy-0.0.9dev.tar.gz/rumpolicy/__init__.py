import logging

from rumgeneric import generic, PredicateBuilder
import prioritized_methods
import peak.rules.core as rules_core
from inspect import isclass

class SecurityDenial(Exception):
    pass
log = logging.getLogger(__name__)

nested_attr='''attr is not None and attr.find('.') >=0'''
class PredicateBuilder(PredicateBuilder):
    def not_nested_attr(self):
        self._conditions.append("""not(%s)""" % (nested_attr,))
class Denial(object):
    """
    An object which is returned by :meth:`Policy.has_permission` when access
    is denied.

    It evaluates to False and holds a message with the reason for the denial
    """
    def __init__(self, msg):
        self.msg = msg

    def __nonzero__(self):
        return False

    def __unicode__(self):
        return unicode(self.msg)

class MultiDenial(Denial):
    def __init__(self, denials):
        self.denials = denials

    def __unicode__(self):
        #TODO: fix internationalization
        #return unicode(policy._(' or ')).join(map(unicode, self.denials))
        return unicode(' or ').join(map(unicode, self.denials))
    
class NotProvided:
    """
    A placeholder for when no optional argument is provided.
    """

class Any(rules_core.Before):
    """
    A Custom method that has special chaining semantics:

    When several of these rules apply then they're all evaluated (with
    no ordering guarantees) and if any of them returns True then access is
    granted. Else a Denial with all denial messages is returned
    """
    def __call__(self, *args, **kw):
        results = []
        for sig, body in self.sorted():
            results.append(body(*args, **kw))
        return any(results) or MultiDenial(results)

# "around" methods always override "any" methods
rules_core.always_overrides(rules_core.Around, Any)
# "any" methods always override "when" methods
rules_core.always_overrides(Any, rules_core.Method)
rules_core.merge_by_default(Any)

add_predicate = Any.make_decorator('add_predicate')
 
def base(string):
    pos = string.find('.')
    return string[:pos]

def remote(string):
    pos = string.find('.')
    return string[pos+1:]

class Policy(object):
    """
    Controls access to resources. It follows the strict design, 
    that every access must be explicitely allowed by conditionally
    applied predicate.
    Predicates  are registered using :meth:`register` for certain kind
    of `obj`, `action`, `attr`. When several rules match
    a given access, then at least one rule must grant the access, by evaluating
    the predicate positively.
    The Policy has to enforced on controller level for granting access to an object.
    It also has be made sure in view factories, that only fields/attributes are displayed, where access
    is granted.
    """


    def check(self, obj, action, attr=None, user=NotProvided):
        """
        Checks if `user` allowed to perform `action` on `obj`? Optional `attr`
        is the name of an attribute from `obj` which if present means the
        query is on that attribute, else it's on the whole `obj`.

        If `user` is :class:`NotProvided` then the currently logged in user
        will be used.

        Raises a :exc:`SecurityDenial` if access is denied
        """
        allowed = self.has_permission(obj, action, attr, user)
        if not allowed:
            raise self.exception_class(unicode(allowed))

    def has_permission(self, obj, action, attr=None, user=NotProvided):
        """
        Is `user` allowed to perform `action` on `obj`? Optional `attr`
        is the name of an attribute from `obj` which if present means the
        query is on that attribute, else it's on the whole `obj`.

        If `user` is :class:`NotProvided` then the currently logged in user
        will be used.

        Returns True or a :class:`Denial` instance.
        """
        return Denial(self._("No permission declared"))

    has_permission.add_predicate = add_predicate.__get__(has_permission)
    


    
    def get_current_user(self):
        raise NotImplementedError
    



        
    @classmethod
    def register(cls, predicate, obj=None, action=None, attr=None, rule=None):
        """
        Registers a `predicate` callable to be evaluated when
        :meth:`has_permission` is called with `obj`, `action`, and `attr` as
        arguments. `predicate` should be a callable that accepts the same
        arguments as :meth:`has_permission` and return True/Denial. Unspecified
        arguments act as wildcards.
        """
        locals_ = {}
        builder = PredicateBuilder(locals_, rule)
        if obj is not None:
            builder.subclass_or_instance("obj", obj)
        if action is not None:
            builder.equals("action", action)
        if attr is not None:
            builder.equals_or_none("attr", attr)

        context = rules_core.ParseContext(predicate, Any.make, locals_, {})
        has_permission = cls.has_permission.im_func
        engine = rules_core.Dispatching(has_permission).engine
        rules = rules_core.rules_for(has_permission)
        rule = rules_core.parse_rule(engine, builder.predicate, context, cls)
        rules.add(rule)
    

    @generic
    def filter(self, resource, query, user=NotProvided):
        """
        Applies extra-filtering criteria to a :class:`rum.interfaces.IQuery` so only
        allowed objects are returned.
        """

    
    @rules_core.around(has_permission, "user is NotProvided")
    #right Policy?
    def __use_current_user(next_method, self, obj, action, attr, user):
        try:
            current_user = self.get_current_user()
        except:
            return Denial(
                self._("No request is available to fetch the current user from")
                )
        return self.has_permission(
            obj=obj, action=action, attr=attr, user=current_user
            )
    
    def fields_for_resource(self, obj):
        from rum import app
        return app.fields_for_resource(obj) or app.fields_for_resource(obj.__class__)
       
    @rules_core.around(has_permission, "user is not NotProvided and "+nested_attr)
    def __handle_nested_attrs(next_method, self, obj, action, attr, user):
        res1=self.has_permission(obj, action, base(attr), user)
        
        if not res1:
            return res1
        res2=self.has_permission(obj, 'join', base(attr), user)
        if not res2:
            return res2
        fields_for_resource= self.fields_for_resource(obj)
        for f in fields_for_resource:
            if f.name ==  base(attr) and hasattr(f, 'other'):
                res3=self.has_permission(f.other,
                    action,
                    remote(attr),
                    user)
                return res3
            
        return Denial('a related field with correct name has to be registered')
    
    
    @filter.around("user is NotProvided")
    def __filter_with_current_user(self, resource, query, user):
        from rum import app
        try:
            current_user = self.get_current_user()
        except:
            current_user = None
        return self.filter(resource, query, current_user)

    @classmethod
    def register_filter(cls, filter, resource=None, rule=None):
        locals_ = {}
        builder = PredicateBuilder(locals_, rule)
        if resource is not None:
            builder.subclass("resource", resource)

        maker = prioritized_methods.PrioritizedMethod.make
        context = rules_core.ParseContext(filter, maker, locals_, {})
        func = cls.filter.im_func
        engine = rules_core.Dispatching(func).engine
        rules = rules_core.rules_for(func)
        rule = rules_core.parse_rule(engine, builder.predicate, context, cls)
        rules.add(rule)



    @filter.when(prio=-1)
    def __no_filter(self, resource, query, user):
        return query
    
    def _(self, string):
        "dummy internationalization"
        return string

    exception_class = SecurityDenial

register = Policy.register


    # except AttributeError:
    #     return Denial('Access to remote resource %s needs to be granted' %(attr,))


# Policy.register(__related_fields_obj, rule='''
# isinstance(attr, basestring) and attr.find('.') >0
#     and attr.find('.') >0
# ''', nested=True)


# Some useful predicates

def not_anonymous(policy, obj, action,  attr, user):
    if user is not None:
        return True
    else:
        return Denial(policy._("Need to authenticate yourself to access this resource"))

def anyone(policy, obj, action,  attr, user):
    return True

filter = Policy.filter.im_func
has_permission = Policy.has_permission

# A dummy default policy that always grants access
class DummyPolicy(Policy): pass
DummyPolicy.register(anyone)
#
