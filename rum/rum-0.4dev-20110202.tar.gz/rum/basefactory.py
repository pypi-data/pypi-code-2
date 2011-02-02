import logging
import weakref
import sys
from itertools import chain, count
from inspect import getargspec, isclass

from peak.util.decorators import frameinfo
from peak.rules import core as rules_core
import prioritized_methods

from rum import util
from rum.genericfunctions import generic, NoApplicableMethods, PredicateBuilder

__all__ = ["BaseFactory", "cache_call"]

log = logging.getLogger(__name__)

class BaseFactory(object):
    """
    Base class for all factories.
    """
    _serial = count()

    def __call__(self, resource, parent=None, **kw):
        """
        Creates an instance of something for the given arguments. If the class
        that we shall instantiate (the one returned by :meth:`get`) accepts
        a `factory` keyword argument the we will pass it a ``wekaref.proxy`` of
        ourselves so it can know who created and access resources with a long
        lifecycle (eg: database connections, etc...) common to all products.
        Arguments used to call the factory will also be tried to be passed to
        the product's constructor.
        """
        kw.update(resource=resource, parent=parent)
        args = kw['args'] = kw.copy()
        args['factory'] = weakref.proxy(self)
        builder = util.adapt_call(self.get, **kw)
        if isclass(builder):
            return util.adapt_call(builder, **args)
        return builder

    @generic
    def get(self, resource, parent=None, **kw):
        """
        I'm a generic function you can extend to return an appropiate builder for
        the factory to use to build its products.

        A keyword argument named ``args`` (which shall be the last positional
        argument) can be a dict that methods around, before or after the main action
        can use to stuff keyword arguments that will be used to call the builder
        that is finally returned. The call will be adapted so it is safe to add
        keyword arguments in the hope they are accepted.
        """


    @classmethod
    def register(cls, builder, resource=None, pred=None, _prio=0, defaults=None,
                 **conds):
        """
        Register ``builder`` as a builder for products of this factory to handle
        resources of type ``resource``.

        This method generates rules to extend :meth:`get`.
        
        Optional parameters:

            `pred`
                A predicate which shall be satisfied for this builder to be chosen
                This argument is a string that will be evaluated in the caller's
                frame.

            `defaults`
                A dict with extra keyword arguments to call the builder with before
                returning the product.

            `prio`
                In the case the predicate that is generated is not more specific than
                anyone registered, this (int) argument will be used to disambiguate.

        Any other keyword argument which is passed will be matched for equality
        against the factory's arguments.
        

        As an example we will create a BaseFactory subclass to produce garments.
        Note that instead of determining temperature in Celsius or Fahrenheit
        we'll have a boolean flag so the example can be followed without a
        calculator. Humidity is in %::
            
            >>> class GarmentFactory(BaseFactory):
            ...     def get(self, resource, is_cold=False, humidity=None, args={}):
            ...         pass
        
        Now we declare some "resources" the factory will create products for::

            >>> class LivingThing(object): pass
            >>> class Person(LivingThing): pass
            >>> class Animal(LivingThing): pass

        Now some products::

            >>> class Garment(object):
            ...     def __init__(self): pass
            ...     def __repr__(self):
            ...         return '<A %s>' % self.__class__.__name__
            >>> class BareSkin(Garment): pass
            >>> class FurCoat(Garment): pass
            >>> class RainCoat(Garment): pass

        Now we register which producs the factory should create and the conditions
        it should create them under::

            >>> # Living things have their bare skin as a default
            >>> GarmentFactory.register(BareSkin, LivingThing)
            >>> # Rather be naked than feel stupid with a FurCoat on a warm day...
            >>> GarmentFactory.register(BareSkin, Person, is_cold=False)
            >>> GarmentFactory.register(FurCoat, Person, is_cold=True)
            >>> # Humidty is a little trickier... we can write a predicate for that
            >>> GarmentFactory.register(RainCoat, Person, "humidity>80", is_cold=True)

        Let's see the products::

            >>> factory = GarmentFactory()
            >>> factory(Animal)
            <A BareSkin>
            >>> factory(Person, is_cold=False)
            <A BareSkin>
            >>> factory(Person, is_cold=True)
            <A FurCoat>
            >>> factory(Person, is_cold=True, humidity=90)
            <A RainCoat>
        
        Now, let's say that we can now invent scuba diving suit::
        
            >>> class ScubaDivingSuit(Garment): pass
        
        And we want to use it when humidity is *exactly* 100%. If we try to register
        it like this::

            >>> # GarmentFactory.register(ScubaDivingSuit, Person, humidity=100)

        We would have seen an ugly traceback from an AmbiguousMethods
        exception. This is because the newly added rule and the rule for
        the conflict since both conditions apply and none is more specific. We have
        two ways of fixing this:
            
            1) Write a more specific rule, that is one with more conditions being
               checked.

            2) Register the new one with a higher priority

        In this case we'll take the easy route::

            >>> GarmentFactory.register(ScubaDivingSuit, Person, humidity=100, _prio=10)
            >>> factory(Person, is_cold=True, humidity=100)
            <A ScubaDivingSuit>
            
        """
        if isinstance(resource, basestring):
            import warnings
            warnings.warn(
                "Passing the predicate as the first positional argument to register()"
                " is deprecated. Please pass it as the 'pred' keyword argument",
                DeprecationWarning, 2
                )
            pred = resource
            resource = None

        if pred:
            assert isinstance(pred, basestring), "Predicate must be a string"
            # Context for predicate dispatch is from caller's frame.
            locals_, globals_ = map(dict.copy, frameinfo(sys._getframe(1))[2:])
        else:
            locals_, globals_ = {}, {}

        # Build a predicate and insert variables needed to parse it into locals_
        pred_builder = PredicateBuilder(locals_, pred)
        if resource is not None:
            pred_builder.subclass("resource", resource)
        for arg, value in conds.iteritems():
            if isclass(value):
                pred_builder.subclass(arg, value)
            elif value is None:
                pred_builder.is_(arg, value)
            else:
                pred_builder.equals(arg, value)
        
        def func(self, *a, **b):
            if defaults:
                # Assumes args is always the last pos. arg
                args = b.get('args', a[-1])
                if isinstance(args, dict):
                    args.update(defaults)
            return builder
        func.func_name = "registered_get_%d" % cls._serial.next()
        func.prio = _prio
        maker = prioritized_methods.PrioritizedMethod.make
        context = rules_core.ParseContext(func, maker, locals_, globals_)
        get = cls.get.im_func
        engine = rules_core.Dispatching(get).engine
        rules = rules_core.rules_for(get)
        rule = rules_core.parse_rule(engine, pred_builder.predicate, context, cls)
        rules.add(rule)
        log.debug("register: rule=%r, predicate=%r", rule, pred_builder.predicate)


    def can_handle(self, resource, parent=None, **kw):
        """
        Returns True if this factory knows how to create products for the given
        arguments.
        """
        try:
            kw['args'] = {}
            self.get(resource, parent, **kw)
            return True
        except NoApplicableMethods:
            return False


def cache_call(next_method, self, *args):
    obj = self._cache.get(args)
    if not obj:
        self._cache[args] = obj = next_method(self, *args)
        log.debug("cache_call: Generated %r: %r", args, obj)
    else:
        log.debug("cache_call: Cache hit for %r: %r", args, obj)
    return obj
