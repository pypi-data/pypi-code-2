import pep362

import unittest
from tests import pep362_fodder
try:
    from tests import pep362_py2_fodder
    from test import test_support
except SyntaxError:
    from tests import pep362_py3k_fodder
    from test import support as test_support
from sys import version_info


def version_specific(major_number):
    def inner(fxn):
        if version_info[0] == major_number:
            return fxn
        else:
            return lambda self: self
    return inner


class ParameterObjectTests(unittest.TestCase):

    """Test the Parameter object."""

    def test_name(self):
        # Test that 'name' attribute works.
        # Must test both using a string and a tuple of strings.
        name = "test"
        param = pep362.Parameter(name, 0)
        self.assertEqual(param.name, name)
        name = ('a', ('b',))
        param = pep362.Parameter(name, 0)
        self.assertEqual(param.name, name)

    def test_position(self):
        # Test the 'position' attribute.
        pos = 42
        param = pep362.Parameter("_", pos)
        self.assertEqual(param.position, pos)

    def test_default_values(self):
        # Testing that 'default_value' is not set is handled in the testing of
        # that attribute.
        default_value = 42
        param = pep362.Parameter('_', 0, True, default_value)
        self.assertEqual(param.default_value, default_value)
        param = pep362.Parameter('_', 0, False)
        self.assertTrue(not hasattr(param, 'default_value'))

    def test_keyword_only(self):
        # Setting the value for keyword_only should create an attribute.
        for value in (True, False):
            param = pep362.Parameter('_', 0, keyword_only=value)
            self.assertEqual(param.keyword_only, value)

    def test_annotations(self):
        # If has_annotation is False then 'annotation' should not exist.
        param = pep362.Parameter('_', 0, has_annotation=False)
        self.assertTrue(not hasattr(param, 'annotation'))
        annotation = 42
        param = pep362.Parameter('_', 0, has_annotation=True,
                                    annotation=annotation)
        self.assertEqual(param.annotation, annotation)


class SignatureObjectTests(unittest.TestCase):

    def test_getitem(self):
        # __getitem__() should return the Parameter object for the name
        # parameter.
        sig = pep362.Signature(pep362_fodder.default_args)
        self.assertTrue(sig['a'])
        param = sig['a']
        self.assertTrue(param.name, 'a')

    def test_iter(self):
        # The iterator should return all Parameter objects in the proper order.
        sig = pep362.Signature(pep362_fodder.default_args)
        params = list(sig)
        self.assertEqual(len(params), 1)
        self.assertEqual(params[0].name, 'a')

    def test_no_args(self):
        # Test a function with no arguments.
        sig = pep362.Signature(pep362_fodder.no_args)
        self.assertEqual('no_args', sig.name)
        self.assertTrue(not sig.var_args)
        self.assertTrue(not sig.var_kw_args)
        self.assertEqual(0, len(list(sig)))

    def test_var_args(self):
        # Test the var_args attribute.
        sig = pep362.Signature(pep362_fodder.var_args)
        self.assertEqual('args', sig.var_args)
        self.assertEqual(0, len(list(sig)))
        sig = pep362.Signature(pep362_fodder.no_args)
        self.assertEqual('', sig.var_args)

    def test_var_kw_args(self):
        # Test the var_kw_args attribute and annotations.
        sig = pep362.Signature(pep362_fodder.var_kw_args)
        self.assertEqual('var_kw_args', sig.name)
        self.assertEqual('kwargs', sig.var_kw_args)
        self.assertEqual(0, len(list(sig)))
        sig = pep362.Signature(pep362_fodder.no_args)
        self.assertEqual('', sig.var_kw_args)

    def test_parameter_positional(self):
        # A function with positional arguments should work.
        sig = pep362.Signature(pep362_fodder.no_default_args)
        self.assertEqual('no_default_args', sig.name)
        param = sig['a']
        self.assertEqual('a', param.name)
        self.assertEqual(0, param.position)
        self.assertTrue(not hasattr(param, 'default_value'))

    def test_parameter_default(self):
        # Default parameters for a function should work.
        sig = pep362.Signature(pep362_fodder.default_args)
        self.assertEqual('default_args', sig.name)
        param = sig['a']
        self.assertEqual('a', param.name)
        self.assertEqual(0, param.position)
        self.assertEqual(42, param.default_value)

    @version_specific(2)
    def test_parameter_tuple(self):
        # A function with a tuple as a parameter should work.
        sig = pep362.Signature(pep362_py2_fodder.tuple_args)
        self.assertEqual('tuple_args', sig.name)
        param = list(sig)[0]
        self.assertTrue(isinstance(param.name, tuple))
        self.assertEqual(('a', ('b',)), param.name)
        self.assertEqual(0, param.position)
        self.assertTrue(not hasattr(param, 'default_value'))

    @version_specific(2)
    def test_parameter_tuple_default(self):
        # A default argument for a tuple parameter needs to work.
        sig = pep362.Signature(pep362_py2_fodder.default_tuple_args)
        self.assertEqual('default_tuple_args', sig.name)
        param = list(sig)[0]
        self.assertEqual(('a', ('b',)), param.name)
        self.assertEqual(0, param.position)
        self.assertEqual((1, (2,)), param.default_value)

    @version_specific(3)
    def test_keyword_only(self):
        # Is a function containing keyword-only parameters handled properly?
        sig = pep362.Signature(pep362_py3k_fodder.keyword_only)
        param = sig['a']
        self.assertEqual(param.name, 'a')
        self.assertTrue(param.keyword_only)
        self.assertEqual(param.position, 0)

    @version_specific(3)
    def test_keyword_only_default(self):
        # Default arguments can work for keyword-only parameters.
        sig = pep362.Signature(pep362_py3k_fodder.keyword_only_default)
        param = sig['a']
        self.assertEqual(param.name, 'a')
        self.assertTrue(param.keyword_only)
        self.assertEqual(param.position, 0)
        self.assertEqual(param.default_value, 42)

    @version_specific(3)
    def test_annotations(self):
        # Make sure the proper annotation is found.
        sig = pep362.Signature(pep362_py3k_fodder.arg_annotation)
        param = sig['a']
        self.assertEqual(param.name, 'a')
        self.assertEqual(param.annotation, int)

    @version_specific(3)
    def test_annotations_default(self):
        # Annotations with a default value should work.
        sig = pep362.Signature(pep362_py3k_fodder.arg_annotation_default)
        param = sig['a']
        self.assertEqual(param.name, 'a')
        self.assertEqual(param.annotation, int)
        self.assertEqual(param.default_value, 42)

    @version_specific(3)
    def test_annotation_keyword_only(self):
        # Keyword-only parameters can have an annotation.
        sig = pep362.Signature(pep362_py3k_fodder.arg_annotation_keyword_only)
        param = sig['a']
        self.assertEqual(param.name, 'a')
        self.assertEqual(param.annotation, int)
        self.assertTrue(param.keyword_only)

    @version_specific(3)
    def test_return_annotation(self):
        # The return value annotation.
        sig = pep362.Signature(pep362_py3k_fodder.return_annotation)
        self.assertEqual(sig.return_annotation, int)

    @version_specific(3)
    def test_var_annotations(self):
        # Annotation on variable arguments (*args & **kwargs).
        sig = pep362.Signature(pep362_py3k_fodder.arg_annotation_var)
        self.assertEqual(sig.var_annotations[sig.var_args], int)
        self.assertEqual(sig.var_annotations[sig.var_kw_args], str)

    def test_signature(self):
        def fresh_func():
            pass
        self.assertTrue(not hasattr(fresh_func, '__signature__'))
        sig = pep362.signature(fresh_func)
        self.assertEqual(sig, fresh_func.__signature__)
        sig2 = pep362.signature(fresh_func)
        self.assertEqual(sig, sig2)
        class FreshClass(object):
            def fresh_method(self):
                pass
        sig = pep362.signature(FreshClass.fresh_method)
        self.assertEqual(sig, FreshClass.fresh_method.__signature__)


class SignatureBindTests(unittest.TestCase):

    """Test Signature.bind()."""

    def test_no_parameters(self):
        sig = pep362.Signature(pep362_fodder.no_args)
        binding = sig.bind()
        self.assertEqual({}, binding)
        self.assertRaises(pep362.BindError, sig.bind, 42)
        self.assertRaises(pep362.BindError, sig.bind, a=0)

    def test_var_parameters(self):
        sig = pep362.Signature(pep362_fodder.var_args)
        binding = sig.bind(0, 1, 2)
        self.assertEqual({'args':(0, 1, 2)}, binding)
        binding = sig.bind()
        self.assertEqual({'args':tuple()}, binding)
        self.assertRaises(pep362.BindError, sig.bind, a=0)

    def test_var_kw_parameters(self):
        sig = pep362.Signature(pep362_fodder.var_kw_args)
        binding = sig.bind(a=0)
        self.assertEqual({'kwargs':{'a':0}}, binding)
        binding = sig.bind()
        self.assertEqual({'kwargs':{}}, binding)
        self.assertRaises(pep362.BindError, sig.bind, 42)

    def test_positional_parameters(self):
        sig = pep362.Signature(pep362_fodder.no_default_args)
        binding = sig.bind(42)
        self.assertEqual({'a':42}, binding)
        binding = sig.bind(a=42)
        self.assertEqual({'a':42}, binding)
        self.assertRaises(pep362.BindError, sig.bind)
        self.assertRaises(pep362.BindError, sig.bind, 0, 1)
        self.assertRaises(pep362.BindError, sig.bind, b=0)

    def test_keyword_parameters(self):
        sig = pep362.Signature(pep362_fodder.default_args)
        binding = sig.bind()
        self.assertEqual({'a':42}, binding)
        binding = sig.bind(0)
        self.assertEqual({'a':0}, binding)
        binding = sig.bind(a=0)
        self.assertEqual({'a':0}, binding)
        self.assertRaises(pep362.BindError, sig.bind, 0, 1)
        self.assertRaises(pep362.BindError, sig.bind, a=0, b=1)
        self.assertRaises(pep362.BindError, sig.bind, b=1)

    @version_specific(2)
    def test_tuple_parameter(self):
        sig = pep362.Signature(pep362_py2_fodder.tuple_args)
        arg = (1, ((2,),))
        binding = sig.bind(arg)
        self.assertEqual({'a':1, 'b':(2,)}, binding)
        self.assertRaises(pep362.BindError, sig.bind, (1,2,3))
        self.assertRaises(pep362.BindError, sig.bind, (1, 2))

    @version_specific(2)
    def test_default_tuple_parameter(self):
        sig = pep362.Signature(pep362_py2_fodder.default_tuple_args)
        binding = sig.bind()
        self.assertEqual({'a':1, 'b':2}, binding)
        arg = (0, (1,))
        binding = sig.bind(arg)
        self.assertEqual({'a':0, 'b':1}, binding)

    @version_specific(2)
    def test_py2_all_args(self):
        sig = pep362.Signature(pep362_py2_fodder.all_args)
        # a, (b, (c,)), d=0, (e, (f,))=(4, (5,)), *g, **h
        # name, position, has_default, default value
        expect = (('a', 0, False, None),
                    (('b', ('c',)), 1, False, None),
                    ('d', 2, True, 0),
                    (('e', ('f',)), 3, True, (4, (5,))))
        self.assertEqual(len(list(sig)), len(expect))
        for param, check in zip(list(sig), expect):
            name, pos, has_default, default_value = check
            self.assertEqual(param.name, name)
            self.assertEqual(param.position, pos)
            if has_default:
                self.assertEqual(param.default_value, default_value)
            else:
                self.assertTrue(not hasattr(param, 'default_value'))
            self.assertTrue(not param.keyword_only)
            self.assertTrue(not hasattr(param, 'annotation'))
        self.assertEqual(sig.var_args, 'g')
        self.assertEqual(sig.var_kw_args, 'h')
        self.assertEqual(len(sig.var_annotations), 0)
        binding = sig.bind(0, (1, (2,)), d=3, i=7)
        expected = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':tuple(),
                    'h':{'i':7}}
        self.assertEqual(expected, binding)

    @version_specific(3)
    def test_keyword_only(self):
        sig = pep362.Signature(pep362_py3k_fodder.keyword_only)
        binding = sig.bind(a=42)
        self.assertEqual(binding, {'a':42})
        self.assertRaises(pep362.BindError, sig.bind)
        self.assertRaises(pep362.BindError, sig.bind, 42)

    @version_specific(3)
    def test_keyword_only_default(self):
        sig = pep362.Signature(pep362_py3k_fodder.keyword_only_default)
        binding = sig.bind()
        self.assertEqual(binding, {'a':42})
        binding = sig.bind(a=1)
        self.assertEqual(binding, {'a':1})
        self.assertRaises(pep362.BindError, sig.bind, 1)

    @version_specific(3)
    def test_all_py3k_args(self):
        # a:int, d=0, *args:int, g:int, h:int=8, **kwargs:int) -> int
        sig = pep362.Signature(pep362_py3k_fodder.all_args)
        # name, position, kw only, has_default, default, has anno, anno
        expected = (('a', 0, False, False, None, True, int),
                    ('d', 1, False, True, 0, False, None),
                    ('g', 2, True, False, None, True, int),
                    ('h', 3, True, True, 8, True, int))
        self.assertEqual(len(list(sig)), len(expected),
                "len(%r) != len(%r)" % ([param.name
                                            for param in sig],
                                        [expect[0] for expect in expected]))
        for param, check in zip(sig, expected):
            name, pos, kw_only, has_default, default, has_anno, anno = check
            self.assertEqual(param.name, name)
            self.assertEqual(param.position, pos)
            if kw_only:
                self.assertTrue(param.keyword_only)
            else:
                self.assertTrue(not param.keyword_only)
            if has_default:
                self.assertEqual(param.default_value, default)
            else:
                self.assertTrue(not hasattr(param, 'default_value'))
            if has_anno:
                self.assertEqual(param.annotation, anno)
            else:
                self.assertTrue(not hasattr(param, 'annotation'))
        self.assertEqual(sig.var_args, 'args')
        self.assertTrue(sig.var_args in sig.var_annotations)
        self.assertEqual(sig.var_annotations[sig.var_args], int)
        self.assertEqual(sig.var_kw_args, 'kwargs')
        self.assertTrue(sig.var_kw_args in sig.var_annotations)
        self.assertEqual(sig.var_annotations[sig.var_kw_args], int)
        self.assertEqual(sig.return_annotation, int)
        binding = sig.bind(0, 3, 6, g=7, i=9)
        expected = {'a':0, 'd':3, 'g':7, 'h':8, 'args':(6,), 'kwargs':{'i':9}}
        self.assertEqual(binding, expected)

    def test_too_many_arguments(self):
        # Only one argument should pair up with a parameter.
        sig = pep362.Signature(pep362_fodder.no_default_args)
        self.assertRaises(pep362.BindError, sig.bind, 1, a=1)


def test_main():
    test_support.run_unittest(ParameterObjectTests,
                                SignatureObjectTests,
                                SignatureBindTests,
                             )


if __name__ == '__main__':
    test_main()
