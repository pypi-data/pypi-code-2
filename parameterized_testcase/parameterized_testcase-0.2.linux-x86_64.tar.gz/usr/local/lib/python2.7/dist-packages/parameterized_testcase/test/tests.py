import unittest

from .. import parameterize

class Echo:
    def test_echo(self):
        return self.param_value

class Llama:
    def test_sound(self):
        return 'A llama says "laga-laga-laga".'

classes = { 'Llama': Llama,
            'Echo': Echo }

params = {
    'alpha': { 'param_value': 42 },
    'beta': { 'param_value': 'decay' },
    }

cases = parameterize(
    [Echo, Llama],
    params)

class Tests(unittest.TestCase):
    def test_count(self):
        '''Created proper amount of testcases.'''
        self.assertEqual(len(cases), 2 * len(params))

    def test_testcase_subclass(self):
        '''Results subclass from TestCase.'''
        for case in cases:
            self.assertTrue(issubclass(case, unittest.TestCase))

    def test_subclasses(self):
        '''Results subclass from original classes.'''
        for case in cases:
            for k,v in classes.items():
                if case.__name__.startswith(k):
                    self.assertTrue(issubclass(case, v))

    def test_param_values(self):
        '''Testcases have proper attribute values.'''
        for case in cases:
            for set_name,param_set in params.items():
                if case.__name__.endswith('_{0}'.format(set_name)):
                    for k,v in param_set.items():
                        self.assertEqual(getattr(case, k), v)
