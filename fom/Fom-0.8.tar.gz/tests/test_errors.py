import unittest

from fom.dev import sandbox_fluid
from fom.errors import (Fluid400Error, Fluid401Error, Fluid404Error,
    Fluid412Error)


class TestNamespaces(unittest.TestCase):
    
    def setUp(self):
        self.fdb = sandbox_fluid()

    def test_delete_412(self):
        self.assertRaises(Fluid412Error,
                          self.fdb.namespaces['test'].delete)

    def test_post_401(self):
        self.assertRaises(Fluid401Error,
                          self.fdb.namespaces['fluiddb'].post, 'fluiddb', 'goo')

    def test_post_404(self):
        self.assertRaises(Fluid404Error,
                          self.fdb.namespaces['{[{[['].post, 'goo', 'goo')

    def test_post_400(self):
        self.assertRaises(Fluid400Error,
                          self.fdb.namespaces[']' * 400].post, 'goo', 'goo')

    def test_get_404(self):
        self.assertRaises(Fluid404Error,
                          self.fdb.namespaces[']]]ss]]'].get)



class TestUsers(unittest.TestCase):
    
    def setUp(self):
        self.fdb = sandbox_fluid()
    
    def test_get_404(self):
        self.assertRaises(Fluid404Error, self.fdb.users['((('].get)


if __name__ == '__main__':
    unittest.main()
