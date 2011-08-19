from .. import parameterize

class Test:
    def test_basic(self):
        self.assertEqual(self.foo, 'foo')
        self.assertEqual(self.className, type(self).__name__)

params = {
    'a': { 'foo': 'foo',
           'className': 'Test_a' },
    'b': { 'foo': 'foo',
           'className': 'Test_b' },
}

cases = list(
    parameterize(
        [Test],
        params))
