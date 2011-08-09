import sys
import unittest

def parameterize(cases, params):
    '''For a sequence of test cases, generate a new sequence of
    unittest.TestCase subclasses, one for each input case
    parameterized for each input parameters set (num. cases x
    num. param sets total.)

    For each input test case this generates a new class, subclassed
    from the original class and ``unittest.TestCase``, but which is
    specialized for a parameter set. Each parameter set is simple a
    dict of names to values, and a class is specialized for a
    parameter set by giving that class a member for each parameter
    name and with the given value. For example, with this input
    class::

      class Foo:
        def bar(self): return x

    and this set of parameters:

      { 'set1' : { 'x' : 3 },
        'set2' : { 'x' : 4 } }

    you would get two new classes based on ``Foo``::

      class Foo_set1(Foo, unittest.TestCase):
        x = 3

      class Foo_set2(Foo, unittest.TestCase):
        x = 4

    Note that the generated classes are injected in the module
    containing the classes from which they are generated.

    Args:
      * cases: The "test-case" objects to parameterize. These do not
          need to be subclasses from ``unittest.TestCase``.
      * params: A dict-of-dicts describing the parameters. The keys of
          the outer dict are parameter-set names, and are used to make
          the names of the generated classes. The keys of the inner
          dicts are class-level members names on the generated
          classes. The values of the inner dicts are the values for
          the class members on the generated classes.

    Returns:
      An iterable over the generated classes.
    '''
    for case in cases:
        case_mod = sys.modules[case.__module__]

        for set_name, param_set in params.items():
            attrs = dict(case.__dict__)
            attrs.update(param_set)
            new_cls = type(
                '{0}_{1}'.format(case.__name__, set_name),
                (case, unittest.TestCase),
                attrs)
            setattr(case_mod, new_cls.__name__, new_cls)
            yield new_cls
