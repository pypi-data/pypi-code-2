import unittest


class Test_write_test_info(unittest.TestCase):

    def _call_FUT(self, cmd, basename, filename):
        from eggtestinfo import write_test_info
        return write_test_info(cmd, basename, filename)

    def test_wo_attrs(self):
        EXPECTED = (
            'test_module = \n'
            'test_suite = \n'
            'test_loader = \n'
            'tests_require = \n'
        )
        cmd = DummyCmd()
        dist = cmd.distribution = DummyDist()
        self._call_FUT(cmd, 'testing', 'test.txt')
        self.assertEqual(len(cmd._wrote), 1)
        self.assertEqual(cmd._wrote[0][0], 'test_info')
        self.assertEqual(cmd._wrote[0][1], 'test.txt')
        self.assertEqual(cmd._wrote[0][2], EXPECTED)

    def test_w_attrs(self):
        EXPECTED = (
            'test_module = foo\n'
            'test_suite = foo.bar\n'
            'test_loader = qux\n'
            'tests_require = baz\n   bam\n'
        )
        cmd = DummyCmd()
        dist = cmd.distribution = DummyDist()
        dist.test_module = 'foo'
        dist.test_suite = 'foo.bar'
        dist.test_loader = 'qux'
        dist.tests_require = ['baz', 'bam']
        self._call_FUT(cmd, 'testing', 'test.txt')
        self.assertEqual(len(cmd._wrote), 1)
        self.assertEqual(cmd._wrote[0][0], 'test_info')
        self.assertEqual(cmd._wrote[0][1], 'test.txt')
        self.assertEqual(cmd._wrote[0][2], EXPECTED)


class DummyDist(object):
    pass


class DummyCmd(object):

    def __init__(self):
        self._wrote = []

    def write_or_delete_file(self, what, filename, text):
        self._wrote.append((what, filename, text))

