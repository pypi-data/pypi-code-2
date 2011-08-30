"""
This module provides four decorators:

  ``prioritized_when``

  ``prioritized_around``

  ``prioritized_before``

  ``prioritized_after``

These behave like their ``peak.rules`` counterparts except that they accept an
optional ``prio`` argument which can be used to provide a comparable object
(usually an integer) that will be used to disambiguate
situations in which more than rule applies to the given arguments and no rule
is more specific than another. That is, situations in which an
``peak.rules.AmbiguousMethods`` would have been raised.

This is useful for libraries which want to be extensible via generic functions
but want their users to easily override a method without figuring out how to
write a more specific rule or when it is not feasible.

For example, TurboJson provides a ``jsonify`` function that looks like this::

    >>> def jsonify(obj):
    ...     "jsonify an object"
    

And extends it so it can handle SqlAlchemy mapped classes in a way
similar to this one::


    >>> from peak.rules import when

    >>> def jsonify_sa(obj):
    ...     print "You're a SA object and I'm going to jsonify you!"

    >>> when(jsonify, "hasattr(obj, 'c')")(jsonify_sa) # doctest: +ELLIPSIS
    <function jsonify_sa at ...>

    >>> class Person(object):
    ...     def __init__(self):
    ...         self.c = "im a stub"

    >>> jsonify(Person())
    You're a SA object and I'm going to jsonify you!

So far so good, however, when a user of the library wants to override the built
in implementation it can become quite hard since they have to write a more
specific rule which can be tedious, for example::

    hasattr(self, 'c') and isinstance(obj, Person)

Notice the ``hasattr`` test, even though ``isinstance(obj, Person)`` implies it,
just to make it more specific than the built in, this gets more cumbersome the
more complicated the expression becomes.

Else this is what happens::

    >>> def jsonify_Person(obj):
    ...     print "No way, I'm going to jsonify you!"

    >>> when(jsonify, (Person,))(jsonify_Person) # doctest: +ELLIPSIS
    <function jsonify_Person at ...>

    >>> try:
    ...     jsonify(Person())
    ... except AmbiguousMethods:
    ...     print "I told you, gfs can sometimes be a pain"
    I told you, gfs can sometimes be a pain


To remedy this situation ``prioritized_when`` can be used to provide an
implementation that will override the one declared with ``when``::

    >>> def jsonify_Person2(obj):
    ...     print "No way, I'm going to jsonify you!"

    >>> prioritized_when(jsonify, (Person,))(jsonify_Person2) # doctest: +ELLIPSIS
    <function jsonify_Person2 at ...>

    >>> jsonify(Person())
    No way, I'm going to jsonify you!

Notice that we didn't need a ``prio`` argument. This is because methods
decorated with ``prioritized_when`` always override those that have been
decorated with ``peak.rules.when``.

Methods decorated with ``prioritized_when`` can also override other methods
that have been decorated by the same decorator using the ``prio`` parameter,
the one which compares greater wins, if both are equal
``AmbiguousMethods`` will be raised as usual.

    >>> def jsonify_Person3(obj):
    ...     print "Don't be so smart, I am, my prio is higher!"

    >>> prioritized_when(jsonify, (Person,), prio=1)(jsonify_Person3) # doctest: +ELLIPSIS
    <function jsonify_Person3 at ...>

    >>> jsonify(Person())
    Don't be so smart, I am, my prio is higher!

For convenience, a ``generic`` decorator is provided too which behaves
like ``peak.rules.dispatch.generic`` except that the ``when``,...,``after``
decorators that will be bound as attributes of the decorated function will be
prioritized::

    >>> @generic
    ... def f(n): pass

    >>> f(5)
    Traceback (most recent call last):
        ...
    NoApplicableMethods: ((5,), {})
    
Add a default rule::

    >>> @f.when()
    ... def default_f(n):
    ...     return n
    >>> f(5)
    5

Add a default rule that overrides the former::

    >>> @f.when(prio=1)
    ... def new_default_f(n):
    ...     return n+1
    >>> f(5)
    6
"""

from peak.util.decorators import decorate_assignment, frameinfo, decorate_class
from peak.util.assembler import with_name
from peak.rules.core import Method, Around, Before, After, abstract,\
                       always_overrides, AmbiguousMethods, Dispatching,\
                       rules_for, parse_rule, combine_actions

from peak.rules.core import clone_function, ParseContext

__all__ = ["prioritized_when", "prioritized_around", "prioritized_after",
           "prioritized_before", "abstract"]


def _get_prio(obj):
    if isinstance(obj, AmbiguousMethods):
        # Give ambiguous methods less priority so around can chain to before
        # and before to when
        return -99999
    return getattr(obj.body, 'prio', 0)

class PrioritizedMixin(object):
    def merge(self, other):
        """
        Merge with other Methods giving priority to the one with the highest
        ``prio`` attribute in the Method's body.

        If both priorities are equal return :exc:`peak.rules.AmbiguousMethods`
        """
        my_prio = _get_prio(self)
        other_prio = _get_prio(other)
        if my_prio < other_prio:
            if other.can_tail:
                return other.tail_with(combine_actions(other.tail, self))
            return other
        elif my_prio > other_prio:
            if self.can_tail:
                return self.tail_with(combine_actions(self.tail, other))
            return self
        return AmbiguousMethods([self,other])

class PrioritizedMethod(PrioritizedMixin, Method):
    """
    A :class:`peak.rules.Method` subclass that will merge ambiguous
    methods giving preference to the one that has the ``prio`` attribute
    in it's body that compares greater.
    """

class PrioritizedAround(PrioritizedMethod):
    """
    A :class:`PrioritizedMethod` subclass that has preference
    over any other :class:`peak.rules.Method`
    """

class PrioritizedBefore(Before, PrioritizedMixin):
    """Method(s) to be called before the primary method(s)"""


class PrioritizedAfter(After, PrioritizedMixin):
    """Method(s) to be called after the primary method(s)"""



# Make sure prioritized override peak's
always_overrides(PrioritizedMethod, Method)
always_overrides(PrioritizedMethod, Around)

# These assign preferences between Prioritizeds
always_overrides(PrioritizedAround, PrioritizedMethod)
always_overrides(PrioritizedAround, PrioritizedBefore)
always_overrides(PrioritizedBefore, PrioritizedAfter)
always_overrides(PrioritizedAfter, PrioritizedMethod)




def make_decorator(cls, name, doc=None, default_prio=0):
    if doc is None:
        doc = "Extend a generic function with a method of type ``%s``" \
              % cls.__name__
    if cls is Method:
        maker = None   # allow gf's to use something else instead of Method
    else:
        maker = cls.make
    def decorate(f, pred=(), depth=2, frame=None, prio=default_prio):
        def callback(cb_frame, name, func, old_locals):
            orig_func = func
            func = clone_function(func)
            assert not hasattr(func, 'prio'),"Oppps"
            func.prio = prio
            real_frame = frame or cb_frame

            rules = rules_for(f)
            engine = Dispatching(f).engine
            kind, module, locals_, globals_ = frameinfo(real_frame)
            context = ParseContext(func, maker, locals_, globals_)
            def register_for_class(cls):
                rules.add(parse_rule(engine, pred, context, cls))
                return cls

            if kind=='class':
                # 'when()' in class body; defer adding the method
                decorate_class(register_for_class, frame=real_frame)
            else:
                register_for_class(None)
            if old_locals.get(name) in (f, rules):
                return f    # prevent overwriting if name is the same
            return orig_func
        return decorate_assignment(callback, depth, frame)
    decorate = with_name(decorate, name)
    decorate.__doc__ = doc
    return decorate



#
# make decorators that accept a prio argument
#

prioritized_when = make_decorator(
    PrioritizedMethod,
    'prioritized_when',
    """
    Extend a generic function with a new action. Optional parameter ``prio``
    can be used to prioritize the new action in case adding it causes an
    :exc:`peak.rules.AmbiguousMethod` exception when the generic function
    is called.
    """
    )

prioritized_around = make_decorator(
    PrioritizedAround,
    'prioritized_around',
    """
    Extend a generic function with a new action. This action will be executed
    before any action registered with ``prioritized_when``.
    Optional parameter ``prio`` can be used to prioritize the new action in
    case adding it causes an ``AmbiguousMethod`` exception when the generic
    function is called.
    """
    )

prioritized_before = make_decorator(PrioritizedBefore, 'prioritized_before')
prioritized_after = make_decorator(PrioritizedAfter, 'prioritized_after')

def generic(func):
    """
    Convenience decorator to bind ``when``, ``around``, ``after`` and
    ``before`` decorators to the decorated function and declareing it as
    ``abstract``.
    """
    func.when = prioritized_when.__get__(func)
    func.around = prioritized_around.__get__(func)
    func.before = prioritized_before.__get__(func)
    func.after = prioritized_after.__get__(func)
    return abstract(func)
