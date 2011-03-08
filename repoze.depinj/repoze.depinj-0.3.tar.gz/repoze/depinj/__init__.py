class DependencyInjector(object):
    def __init__(self):
        self.factories = {}
        self.lookups = {}
        self.factory_results = {}

    def inject_factory(self, fixture, real):
        """ Inject a testing dependency factory.  ``fixture`` is the
        factory used for testing purposes.  ``real`` is the actual
        factory implementation when the system is not used under test.
        Returns a ``promise`` callable, which accepts no arguments.
        When called, the promise callable returns the instance created
        during a test run."""
        def thunk():
            return self.factory_results[(thunk, real)]
        these_factories = self.factories.setdefault(real, [])
        these_factories.append((thunk, fixture))
        return thunk

    def inject(self, fixture, real):
        """ Inject a testing dependency object.  ``fixture`` is the
        object used for testing purposes.  ``real`` is the
        actual object when the system is not used under test."""
        these_lookups = self.lookups.setdefault(_key(real), [])
        these_lookups.append(fixture)

    def construct(self, real, *arg, **kw):
        """ Return the result of a testing factory related to ``real``
        when the system is under test or the result of the ``real``
        factory when the system is not under test.  ``*arg`` and
        ``**kw`` will be passed to either factory."""
        if real in self.factories:
            these_factories = self.factories[real]
            if these_factories:
                thunk, fake = these_factories.pop(0)
                result = fake(*arg, **kw)
                self.factory_results[(thunk, real)] = result
                return result
        return real(*arg, **kw)

    def lookup(self, real):
        """ Return a testing object related to ``real`` if the system
        is under test or the ``real`` when the system is not under
        test."""
        key = _key(real)
        if key in self.lookups:
            these_lookups = self.lookups[key]
            if these_lookups:
                fake = these_lookups.pop(0)
                return fake
        return real

    def clear(self):
        """ Clear the dependency injection registry """
        self.__init__()


def _key(obj):
    """
    Makes a key from an object suitable for looking up.  If object is hashable
    just returns the object, otherwise returns id.
    """
    try:
        hash(obj)
        return obj
    except TypeError:
        return id(obj)


injector = DependencyInjector()
lookup = injector.lookup
construct = injector.construct
inject_factory = injector.inject_factory
inject = injector.inject
clear = injector.clear

